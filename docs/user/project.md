# Open Standards Lab Projects

A Standards Lab project's provides a workspace to develop JSON schemas and test data with these schemas.

## Project Settings

### Owner
This is a read-only field which displays whether you are a project owner. Project owners have full privileges to change any settings, schema or data.

### Modified

When the project's settings were last modified.

### Name

The current project name. Project names must only contain characters A-Z, a-z, 0-9 , - and _.

To create a copy of the project change the name and click 'Save As New Project'. All settings, schema and data will be copied to the new project.

### Editable by anyone with the link

Give Owner level permissions to anyone with access to the project.


### Top-Level key name for the list of the data

In data standards that support spreadsheets as a format the contents of the spreadsheet will need to be nested under a particular key name.

For example entering `examples` will mean that any spreadsheet data uploaded to the system will be converted to JSON data with a top-level key of `examples`.

Example resulting data:
```JSON

{
    "examples": [
        {"object": 1},
        {"object": 0}
    ]
}

```

[Further documentation can be found in the developing standards documentation](https://os4d.opendataservices.coop/patterns/schema/#pattern-top).

## Schema

Edit an existing JSON schema file by using the "Upload schema file" button and selecting the file for opening. Once uploaded the schema file will be available to be opened in the editor.

Edit a new file by setting the file name using the "File open" text entry. This is set to "schema.json" by default.

Use the "Save schema" button to save any changes.

### Schema file management

The schema files in the project will appear in a list.

Each file can be opened in the editor by clicking on the file name.

Use the drop down menu to "Download" or "Delete" a file. If there are multiple schema files you will need to set which file is the root schema by using the menu item "Set as Root Schema", the default is the first schema file uploaded.

#### Root Schema

The root schema in a project is the top-level schema which either contains the whole schema or references other schemas being used. For example:

```JSON
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "title": "An Example root schema",
  "type": "object",
  "required": [
    "examples"
  ],
  "properties": {
    "examples": {
      "type": "array",
      "minItems": 1,
      "items": {
        "$ref": "https://example.com/schema/example-items-schema.json"
      },
      "uniqueItems": true
    }
  }
}
```

### Schema editor

The schema editor supports multiple views and modes for editing JSON. The default is set to "Tree".

Changes in the editor are only saved once the "Save Schema" button is pressed.

## Data

Edit a new file by setting the file name using the "File open" text entry. This is set to "untitled.json" by default.

Edit existing files use the Upload data button. Supported formats: Comma-Separated Values (.csv), JSON (.json), Microsoft Excel (.xlsx) or Open spreadsheet format (.ods).

Editing is supported for JSON files and CSV files.

Each file can be opened in the editor by clicking on the file name.

### Data editor

The data editor supports multiple views and modes for editing JSON. The default is set to "Code".

Changes in the editor are only saved once the "Save Data" button is pressed.

### Data file management

Use the drop down menu to "Download" or "Delete" a file.

## Test

To test the data in the project against the schema click "Start Test". Once the test is complete a summary for each data file will be displayed. Full test results are available by clicking "View Result Details".
