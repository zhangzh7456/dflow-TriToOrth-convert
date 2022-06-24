# dflow OP cutter

Cookie cutter recipe for [dflow](https://github.com/deepmodeling/dflow) OP. The fastest way to template a new dflow OP package.

For the package structure produced by the OP cutter, see the [dflow-hello](https://github.com/zjgemi/dflow-hello) demo OP.

## Usage instructions

```
$ pip install cookiecutter
$ cookiecutter https://github.com/deepmodeling/dflow-op-cutter.git
package_name [dflow-hello]: 
module_name [dflow_hello]: 
short_description [dflow demo OP]: 
github_user [deepmodeling]: 
github_repo [dflow-hello]: 
contact_email []: 
version [0.1.0]: 
author [deepmodeling]: 
dflow_min_version [1.0]: 
dockerhub_user [deepmodeling]: 
dockerhub_repo [dflow-hello]: 
```

This will produce the files and folder structure for your OP package,
already adjusted for the name of your OP.

You are now ready to start development!
See the `README.md` of your package (or of [dflow-hello](https://github.com/zjgemi/dflow-hello)) for an explanation of the purpose of all generated files.
