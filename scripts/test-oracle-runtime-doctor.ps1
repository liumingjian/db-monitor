$ErrorActionPreference = "Stop"

uv run python -c "import oracledb; print(oracledb.__version__)"
docker compose up -d postgres oracle-xe

try {
    $oracleContainer = (docker compose ps -q oracle-xe).Trim()
    docker exec $oracleContainer bash --noprofile --norc -lc "export ORACLE_HOME=/u01/app/oracle/product/11.2.0/xe; export PATH=`"$ORACLE_HOME/bin:`$PATH`"; export LD_LIBRARY_PATH=`"$ORACLE_HOME/lib`"; echo 'select 1 from dual;' | sqlplus -s system/oracle@//127.0.0.1:1521/XE"
}
finally {
    docker compose stop postgres oracle-xe
}
