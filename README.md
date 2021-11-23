# add_template_documentation_sub
Adds the {{documentation subpage}} tag to Template Subpages.

## Class variables for customization
### TEMPLATE
The template that will be used to tag pages (e.g. `{{documentation subpage}}`).

### NAMESPACE
The namespace that the program will extract pages from (e.g. 0 for (Main)).\
https://www.mediawiki.org/wiki/Manual:Namespace#Built-in_namespaces to see available namespaces.

### PAGES_LIMIT
The number of pages that will be extracted at a time. Used in get_params() in params for "aplimit".

### REV_PAGE
The page that the program reads and writes the last page title to continue from.

### DEVELOPMENT_ENV
A toggle for https validation. 