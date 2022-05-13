# User Guide on How to Test the Vault Helper Tool

## How to run
Ensure that you have followed the commands in `install-docker.md` to initialize Candigv2 with docker, then run 
```
make compose
make init-authx
```
After this, look at the `keys.txt` file in the vault folder to find the root access token. This token will need to be updated in the `token.txt` file in the root directory.
Then either run
```
go install -v https://github.com/CanDIG/Vault-Helper-Tool
```
or run the following commands from the root of the Candigv2 repo to copy over the binary file. (This is necessary since the paths in the settings are configured to work for Candigv2).
```
cd lib/vault/Vault-Helper-Tool/cli \
go build \
cd - \
cp lib/vault/Vault-Helper-Tool/cli/cli .
```
From the root of the `Candigv2` repository, run 
```
./cli {command} {optional-arguments}
```
## How to use Tool

- To call `write`, use:
```
./cli write {json file}
```
or after running the cli as 
```
write {json file}
```

- To call `read`, use:

```
./cli read {user's name}
```
or after running the cli as 
```
read {user's name}
```

- To call `delete`, use:
```
./cli delete {user's name}
```
or after running the cli as
```
delete {user's name}
```

- To call `list`, use:

```
./cli list
``` 
or after running the cli as 
```
list 
```

- To call `updateRole`, use:
```
$ ./cli updateRole {path-to-json-for-role} {role}
```
or after running the cli as 
```
updateRole {path-to-json-for-role} {role}
```

- To call `help`, use:

```
./cli -h
``` 
or after running the cli as 
```
./cli 
```

## Examples for Proper usage
- Write:
```
$ ./cli write Vault-Helper-Tool/example.json
Secret written successfully.
```
- Read:
```
$ ./cli read entity_1cd0efa6
Connecting to Vault using token in token.txt
{"dataset123":"4","dataset321":"4"}
```
- Delete:
```
$ ./cli delete entity_1cd0efa6
User deleted successfully.
```
- List: 
```
$ ./cli list
Connecting to Vault using token in token.txt
entity_1cd0efa6
{"dataset123":"4","dataset321":"4"}
-------------------------
entity_c65b1f1a
{"dataset123":"1","dataset321":"1"}
-------------------------
```
- updateRole
```
$ ./cli updateRole researcher Vault-Helper-Tool/role.json
Connecting to Vault using token in token.txt
Role updated successfully.
```
## How to Trigger Errors

### Incorrect number of arguments
```
$ ./cli write
Connecting to Vault using token in token.txt
2022/04/12 05:49:59 middleware errored: validation failed: file name not provided
```

```
$ ./cli read
Connecting to Vault using token in token.txt
2022/04/12 05:49:32 middleware errored: validation failed: no arguments provided, missing user's name
```

```
./cli delete
Connecting to Vault using token in token.txt
2022/04/12 05:50:35 middleware errored: validation failed: no arguments provided, missing user's name
```
```
./cli updateRole
Connecting to Vault using token in token.txt
2022/04/12 05:50:35 middleware errored: validation failed: no arguments provided, missing filename
```

### Wrong file name
```
$ ./cli write non-file.json
Connecting to Vault using token in token.txt
2022/04/12 05:53:07 middleware errored: handling failed: could not open file. open non-file.json: no such file or directory

```

### User/Role does not exist in vault

```
$ ./cli read non-user
Connecting to Vault using token in token.txt
2022/04/12 05:52:36 middleware errored: handling failed: non-user does not exist in Vault.
```

```
$ ./cli delete non-user
Connecting to Vault using token in token.txt
2022/04/14 10:43:15 middleware errored: handling failed: non-user does not exist in Vault.

```

```
$ ./cli ur Vault-Helper-Tool/non-role.json researcher
Connecting to Vault using token in token.txt
2022/04/19 08:20:39 middleware errored: handling failed: could not open file. open Vault-Helper-Tool/non-role.json: no such file or directory

```