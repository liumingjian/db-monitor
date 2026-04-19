async page => {
  const ARTIFACT_DIR = 'artifacts/todomvc-playwright';
  const SCREENSHOT_DIR = `${ARTIFACT_DIR}/screenshots`;
  const VIEWPORT = { width: 1440, height: 1000 };
  const APP_URL = 'https://demo.playwright.dev/todomvc/';
  const TODO_TITLES = ['Buy milk', 'Write tests', 'Review logs'];
  await page.setViewportSize(VIEWPORT);

  const normalizeName = value =>
    value
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');

  const getTodoItems = () => page.locator('.todo-list li');
  const getTodoTexts = async () => {
    const texts = await getTodoItems().locator('label').allTextContents();
    return texts.map(text => text.trim());
  };

  const assertEqual = (actual, expected, message) => {
    if (actual !== expected) {
      throw new Error(`${message}. Expected "${expected}" but received "${actual}"`);
    }
  };

  const assertDeepEqual = (actual, expected, message) => {
    const actualValue = JSON.stringify(actual);
    const expectedValue = JSON.stringify(expected);
    if (actualValue !== expectedValue) {
      throw new Error(`${message}. Expected ${expectedValue} but received ${actualValue}`);
    }
  };

  const assertVisibleCount = async (locator, expected, message) => {
    const count = await locator.count();
    assertEqual(count, expected, message);
  };

  const resetApp = async () => {
    await page.goto(APP_URL, { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('networkidle');
    await page.evaluate(() => localStorage.clear());
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('networkidle');
  };

  const addTodo = async title => {
    const input = page.locator('.new-todo');
    await input.fill(title);
    await input.press('Enter');
  };

  const addTodos = async titles => {
    for (const title of titles) {
      await addTodo(title);
    }
  };

  const readCounter = async () => {
    const text = await page.locator('.todo-count').textContent();
    return text.replace(/\s+/g, ' ').trim();
  };

  const saveScenarioShot = async (name, status) => {
    const fileName = `${status}-${normalizeName(name)}.png`;
    const fullPath = `${SCREENSHOT_DIR}/${fileName}`;
    await page.screenshot({ path: fullPath, fullPage: true });
    return fullPath;
  };

  const scenarioResults = [];

  const runScenario = async (name, testFn, expectedStatus = 'passed') => {
    await resetApp();
    let actualStatus = 'passed';
    let errorMessage = null;

    try {
      await testFn();
      if (expectedStatus === 'failed') {
        actualStatus = 'failed';
        errorMessage = 'Scenario was expected to fail, but it passed.';
      }
    } catch (error) {
      errorMessage = error instanceof Error ? error.message : String(error);
      actualStatus = expectedStatus === 'failed' ? 'failed' : 'error';
    }

    const screenshotPath = await saveScenarioShot(name, actualStatus);
    scenarioResults.push({
      name,
      expectedStatus,
      actualStatus,
      screenshotPath,
      errorMessage,
    });
  };

  await runScenario('initial load is empty', async () => {
    await assertVisibleCount(getTodoItems(), 0, 'Initial load should not render todo items');
    const header = await page.locator('.header h1').textContent();
    assertEqual(header.trim(), 'todos', 'Header text should match');
    const placeholder = await page.locator('.new-todo').getAttribute('placeholder');
    assertEqual(placeholder, 'What needs to be done?', 'Input placeholder should match');
  });

  await runScenario('add items and update counter', async () => {
    await addTodos(TODO_TITLES);
    await assertVisibleCount(getTodoItems(), 3, 'Three todos should exist');
    const counter = await readCounter();
    assertEqual(counter, '3 items left', 'Counter should reflect three active items');
    const texts = await getTodoTexts();
    assertDeepEqual(texts, TODO_TITLES, 'Todo texts should match the added items');
  });

  await runScenario('complete item and filter active', async () => {
    await addTodos(TODO_TITLES);
    await getTodoItems().nth(1).locator('.toggle').check();
    const completedClass = await getTodoItems().nth(1).getAttribute('class');
    if (!completedClass.includes('completed')) {
      throw new Error('Completed item should have completed class');
    }
    const counter = await readCounter();
    assertEqual(counter, '2 items left', 'Counter should decrement after completion');
    await page.getByRole('link', { name: 'Active' }).click();
    const visibleTexts = await getTodoTexts();
    assertDeepEqual(
      visibleTexts,
      ['Buy milk', 'Review logs'],
      'Active filter should hide the completed item'
    );
  });

  await runScenario('completed filter and clear completed', async () => {
    await addTodos(TODO_TITLES);
    await getTodoItems().nth(0).locator('.toggle').check();
    await page.getByRole('link', { name: 'Completed' }).click();
    const visibleTexts = await getTodoTexts();
    assertDeepEqual(visibleTexts, ['Buy milk'], 'Completed filter should only show completed items');
    await page.getByRole('button', { name: 'Clear completed' }).click();
    await page.getByRole('link', { name: 'All' }).click();
    const remainingTexts = await getTodoTexts();
    assertDeepEqual(
      remainingTexts,
      ['Write tests', 'Review logs'],
      'Clearing completed should remove finished items'
    );
  });

  await runScenario('edit delete and persist after reload', async () => {
    await addTodos(TODO_TITLES);
    const secondItem = getTodoItems().nth(1);
    await secondItem.dblclick();
    const editInput = secondItem.locator('.edit');
    await editInput.fill('Write better tests');
    await editInput.press('Enter');
    let texts = await getTodoTexts();
    assertDeepEqual(
      texts,
      ['Buy milk', 'Write better tests', 'Review logs'],
      'Editing should update the todo title'
    );

    const thirdItem = getTodoItems().nth(2);
    await thirdItem.hover();
    await thirdItem.locator('.destroy').click();
    texts = await getTodoTexts();
    assertDeepEqual(
      texts,
      ['Buy milk', 'Write better tests'],
      'Deleting should remove the hovered item'
    );

    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('networkidle');
    texts = await getTodoTexts();
    assertDeepEqual(
      texts,
      ['Buy milk', 'Write better tests'],
      'Todos should persist after reload'
    );
  });

  await runScenario(
    'intentional failure expecting clear completed before completion',
    async () => {
      await addTodos(['Only task']);
      const buttonCount = await page.getByRole('button', { name: 'Clear completed' }).count();
      assertEqual(buttonCount, 1, 'Clear completed button should be visible immediately');
    },
    'failed'
  );

  await runScenario(
    'intentional failure expecting blank todo submission to create item',
    async () => {
      await addTodos(['   ']);
      await assertVisibleCount(getTodoItems(), 1, 'Blank submission should create a todo item');
    },
    'failed'
  );

  return {
    artifactDir: ARTIFACT_DIR,
    reportPath: `${ARTIFACT_DIR}/report.json`,
    scenarios: scenarioResults,
  };
}
