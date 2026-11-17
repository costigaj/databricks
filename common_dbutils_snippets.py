# =====================================================================
# Databricks Utilities (dbutils) Common Operations Reference Guide
# =====================================================================
# This script contains commonly used dbutils code snippets for Databricks
# notebooks, covering File System (fs), Notebook workflows (notebook),
# Interactive Widgets (widgets), Secrets Management (secrets), and Library
# utilities.

# ---------------------------------------------------------------------
# 1. FILE SYSTEM UTILITIES (dbutils.fs)
# ---------------------------------------------------------------------
# Works seamlessly with Unity Catalog Volumes (/Volumes/...) and DBFS paths.

# List files and subdirectories in a Unity Catalog Volume
files = dbutils.fs.ls("/Volumes/databricksac/bronze/raw_files")
display(files)

# Create a directory (creates parent directories if needed)
dbutils.fs.mkdirs("/Volumes/databricksac/bronze/raw_files/archive/2026")

# Copy a file or directory (set recurse=True for directories)
dbutils.fs.cp(
    "/Volumes/databricksac/bronze/raw_files/sample_data.csv",
    "/Volumes/databricksac/bronze/raw_files/archive/2026/sample_data.csv"
)

# Move / rename a file or directory
dbutils.fs.mv(
    "/Volumes/databricksac/bronze/raw_files/temp_data.csv",
    "/Volumes/databricksac/bronze/raw_files/processed_data.csv"
)

# Preview the first N bytes of a file (great for checking CSV headers/delimiters)
print(dbutils.fs.head("/Volumes/databricksac/bronze/raw_files/sample_data.csv", maxBytes=500))

# --- Removing Files and Folders (Permanent Deletion) ---
# Remove a single file
# dbutils.fs.rm("/Volumes/databricksac/bronze/raw_files/temp_data.csv")

# Remove an entire folder and all its contents (set recurse=True)
# dbutils.fs.rm("/Volumes/databricksac/bronze/raw_files/temp_folder", recurse=True)

# Remove files matching a wildcard (*) pattern
# dbutils.fs.rm("/Volumes/databricksac/bronze/raw_files/*_old.csv")


# ---------------------------------------------------------------------
# 2. NOTEBOOK WORKFLOWS (dbutils.notebook)
# ---------------------------------------------------------------------
# Chain notebooks together for modular Medallion orchestration.

# Run a child notebook with a timeout (in seconds) and pass parameters
# result = dbutils.notebook.run(
#     path="./02_silver_customers_upsert",
#     timeout_seconds=600,
#     arguments={"env": "prod", "load_date": "2026-11-17"}
# )
# print(f"Child notebook returned: {result}")

# Exit the current notebook early and return a status string to a caller/job
# dbutils.notebook.exit("SUCCESS: 1,250 rows merged into silver.customers_enr")


# ---------------------------------------------------------------------
# 3. INTERACTIVE WIDGETS (dbutils.widgets)
# ---------------------------------------------------------------------
# Parameterize notebooks so they can run interactively or via Databricks Jobs.

# Create a free-text input widget with a default value
dbutils.widgets.text("target_catalog", "databricksac", "Target Catalog")

# Create a dropdown selection widget
dbutils.widgets.dropdown("environment", "dev", ["dev", "staging", "prod"], "Environment")

# Retrieve the current value of a widget
catalog_name = dbutils.widgets.get("target_catalog")
env_name = dbutils.widgets.get("environment")
print(f"Running in {env_name} using catalog: {catalog_name}")

# Retrieve all widget values as a Python dictionary
all_params = dbutils.widgets.getAll()

# Remove a specific widget or clear all widgets from the notebook UI
# dbutils.widgets.remove("environment")
# dbutils.widgets.removeAll()


# ---------------------------------------------------------------------
# 4. SECRETS MANAGEMENT (dbutils.secrets)
# ---------------------------------------------------------------------
# Safely retrieve API keys, JDBC passwords, or storage tokens without hardcoding.

# List all available secret scopes
# scopes = dbutils.secrets.listScopes()
# display(scopes)

# List secret keys within a specific scope (values remain hidden)
# keys = dbutils.secrets.list(scope="my_api_scope")
# display(keys)

# Retrieve a secret value (Databricks automatically redacts it in notebook output)
# api_key = dbutils.secrets.get(scope="my_api_scope", key="external_service_token")


# ---------------------------------------------------------------------
# 5. HELP & DISCOVERY
# ---------------------------------------------------------------------

# Display built-in documentation for any dbutils module or command
dbutils.fs.help()
# dbutils.fs.help("cp")
# dbutils.widgets.help()
# dbutils.notebook.help()
