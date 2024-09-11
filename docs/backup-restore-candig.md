# Backing up and restoring CanDIG data

There are three kinds of data stored in CanDIG that we recommend backing up regularly.
1. Clinical and Genomic metadata stored in CanDIGs's postgres databases
2. Authorization data stored in vault that details user's authorization to access/edit ingested data
3. Logs

For data types 1 and 2, we recommend taking back ups after each ingest event and to store one or more copies of your backups on a separate secure server from your CanDIG installation. We also recommend encrypting your backup so that it cannot be accessed by an unauthorizaed user.

Logs can be backed up on a regular schedule and at a minimum, should be saved elsewhere when performing a rebuild of the stack.

## Backing up postgres databases

Both clinical and genomic metadata are stored within databases running in the postgres container `postgres-db`. 

The commands below assume that you are connected to the machine that is hosting the dockerized CanDIGv2 stack.

To backup the data stored in these databases:

1. Open an interactive terminal inside the running postgres docker container with:

```bash
docker exec -it candigv2_postgres-db_1 bash
```

1. Dump contents of the two databases to files. `-d` specifies the database to dump, `-f` specifies the filename. Below we use the date and the name of the database being backed up:

```bash
pg_dump -U admin -d genomic -f yyyy-mm-dd-genomic-backup.sql
pg_dump -U admin -d clinical -f yyyy-mm-dd-clinical-backup.sql
```

You should then have two files, each with a complete copy of each of the databases. 

You can now exit the container by entering

```bash
exit
```

You should copy these to a secure location outside of the running container and consider encrypting them or otherwise ensuring that unauthorized users will not have access to the information. To copy from the container on to the docker host, you can use a command similar to: 

```bash
docker cp candigv2_postgres-db_1:yyyy-mm-dd-genomic-backup.sql /desired/path/target
docker cp candigv2_postgres-db_1:yyyy-mm-dd-clinical-backup.sql /desired/path/target
```

## Restoring postgres databases

To restore the databases that we have backed up, assuming you have the CanDIG stack up and running 

1. Stop the running katsu and htsget containers which are connected to the databases

```bash
docker stop candigv2_katsu_1
docker stop candigv2_htsget_1
```

1. Then we need to copy the `sql` backup files into the running postgres container

```bash
docker cp /path/to/backup/yyyy-mm-dd-genomic-backup.sql candigv2_postgres-db_1:/yyyy-mm-dd-genomic-backup.sql
docker cp /path/to/backup/yyyy-mm-dd-clinical-backup.sql candigv2_postgres-db_1:/yyyy-mm-dd-clinical-backup.sql
```

Next we need to delete the initialized databases so we can replace them with the backed up versions. 

1. Open an interactive terminal to the postgres container

```bash
docker exec -it candigv2_postgres-db_1 bash
```

1. Then connect to the psql commandline prompt with a database other than the ones we want to drop:

```bash
psql -U admin -d template1
```

1. Then drop the two existing databases, create empty replacement databases then quit the psql commandline prompt

```bash
DROP DATABASE clinical;
CREATE DATABASE clinical;
DROP DATABASE genomic;
CREATE DATABASE genomic;
\q
```

1. Load the backed up copies from file with these commands:

```bash
psql -U admin -d clinical < yyyy-mm-dd-clinical-backup.sql
psql -U admin -d genomic < yyyy-mm-dd-genomic-backup.sql
```

1. Exit the interactive terminal with the `exit` command.

1. Restart the katsu and htsget services

```bash
docker start candigv2_katsu_1
docker start candigv2_htsget_1
```

You should be able to see the restored data in the data portal.

## Backing up Authorization data

## Backing up logs

Logs are stored in `tmp/logging`. The contents of this folder should be saved periodically.


