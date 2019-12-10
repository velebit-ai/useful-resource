# useful-resource

The purpose of function `useful.resource.load` is to provide unified access and parsing for resources on various locations. The usage is extremely simple:

```python
import useful.resource

config = useful.resource.load('s3://bucket/config.yaml')
```

We achieve this unified access in multiple stages:

## 1. Scheme and format extraction

The only information we must have before we start is an URI for an object we want to access. Using URI `<schema>://<string>.<extension>` we can easily extract schema/protocol and format/extension.

## 2. Accessing and reading the resource

In this step, depending on the schema, we provide a `Reader` object that implements method `Reader.open()`. This provides a file-like object and allows us to read data byte by byte, in the same way as built-in function `open()` does for local files. Currently we support multiple schemas
 * `s3://` - AWS S3 storage
 * `gs://` - Google Cloud Storage
 * `file://` - local storage
 * `<no schema>` - local storage

but more can be easily added by editing `useful.resource.readers.readers` dictionary, a schema to reader implementation mapping. `useful.resource.load` function uses result caching with invalidation based on file changes. That is the reason we also implement method `Reader.hash()` which is also used to calculate object checksum without reading/downloading the whole resource. See step (4) for more details.

## 3. Parsing the actual data

From step (2) we have a file-like object and now we want to parse the data inside. In the step (1) we extracted the format/extension and now we can use a `Parser` object to actually parse the data. At the moment we only support:

 * `.json` - JSON format
 * `.yaml` - YAML format
 * `.yml` - YAML format
 * `.pkl` - Python pickle format
 * `<anything else>` - raw binary data

but more can be easily added by editing `useful.resource.parsers.parsers` dictionary, an extension to parser implementation mapping.

## 4. [Optional] hook

Let's say we wanted to initialize our object `Model` with pretrained weights stored in a file `s3://bucket/weights.json`. Both downloading the weights and loading them into the program are slow because we are working with large models. This is why we need to avoid downloading the resource again if we can. We do this by checking the return value after calling `Reader.hash()`. Since we also want to avoid frequent loading of weights into our model, we want to cache the `Model` instance itself, instead of raw weights resource. This is where `hook` comes in. `hook` is an optional argument for the function `useful.resource.load`. It is a `callable` that accepts the output from the step (3) and runs additional modification and/or creation of objects instances. In our example, we would simply run

```python
model = useful.resource.load('s3://bucket/weights.json', hook=Model)
```

