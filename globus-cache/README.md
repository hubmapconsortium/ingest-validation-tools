Typically, there will be lots of little fixes in the local metadata.tsv,
while the files on Globus will be stable. When you do specify a Globus origin
and path, it will be cached here, so it doesn't need to be re-downloaded.
Most files are represented by an empty placeholder, but any metadata TSVs
are downloaded in their entirety.
