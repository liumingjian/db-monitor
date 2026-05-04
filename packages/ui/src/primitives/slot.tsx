import {
	Children,
	type HTMLAttributes,
	type ReactElement,
	type Ref,
	cloneElement,
	forwardRef,
	isValidElement,
} from "react";
import { cn } from "./utils";

type AnyProps = Record<string, unknown>;

const mergeRefs =
	<T,>(...refs: Array<Ref<T> | undefined>) =>
	(value: T | null) => {
		for (const ref of refs) {
			if (typeof ref === "function") {
				ref(value);
			} else if (ref && typeof ref === "object") {
				(ref as { current: T | null }).current = value;
			}
		}
	};

const mergeProps = (slotProps: AnyProps, childProps: AnyProps): AnyProps => {
	const merged: AnyProps = { ...childProps };
	for (const key of Object.keys(slotProps)) {
		const slotValue = slotProps[key];
		const childValue = childProps[key];
		if (key === "className") {
			merged.className = cn(slotValue as string, childValue as string);
		} else if (key === "style") {
			merged.style = { ...(slotValue as object), ...(childValue as object) };
		} else if (typeof slotValue === "function" && typeof childValue === "function") {
			merged[key] = (...args: unknown[]) => {
				(childValue as (...a: unknown[]) => unknown)(...args);
				(slotValue as (...a: unknown[]) => unknown)(...args);
			};
		} else if (childValue === undefined) {
			merged[key] = slotValue;
		}
	}
	return merged;
};

export interface SlotProps extends HTMLAttributes<HTMLElement> {
	children?: React.ReactNode;
}

export const Slot = forwardRef<HTMLElement, SlotProps>((props, ref) => {
	const { children, ...slotProps } = props;
	if (!isValidElement(children)) {
		return null;
	}
	const child = Children.only(children) as ReactElement<AnyProps> & {
		ref?: Ref<HTMLElement>;
	};
	const childRef = (child as { ref?: Ref<HTMLElement> }).ref;
	const merged = mergeProps(slotProps as AnyProps, child.props as AnyProps);
	merged.ref = mergeRefs(ref, childRef);
	return cloneElement(child, merged);
});
Slot.displayName = "Slot";
