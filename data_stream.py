import logging
import json
from pyspark.sql import SparkSession
from pyspark.sql.types import *
import pyspark.sql.functions as psf
from dateutil.parser import parse as parse_date
from datetime import datetime


# TODO Create a schema for incoming resources
schema = StructType([StructField("crime_id", StringType(), True),
                     StructField("original_crime_type_name", StringType(), True),
                     StructField("report_date", TimestampType(), True),
                     StructField("call_date", TimestampType(), True),
                     StructField("offense_date", TimestampType(), True),
                     StructField("call_time", StringType(), True),
                     StructField("call_date_time", TimestampType(), True),
                     StructField("disposition", StringType(), True),
                     StructField("address", StringType(), True),
                     StructField("city", StringType(), True),
                     StructField("state", StringType(), True),
                     StructField("agency_id", IntegerType(), True),
                     StructField("address_type", StringType(), True),
                     StructField("common_location", StringType(), True)
                    ])

# TODO create a spark udf to convert time to YYYYmmDDhh format
@psf.udf(StringType())
def udf_convert_time(timestamp):
    return (datetime.strptime(timestamp, '%YYYY%mm%DD%hh'), StringType())

def run_spark_job(spark):

    # TODO Create Spark Configuration
    # Create Spark configurations with max offset of 200 per trigger
    # set up correct bootstrap server and port
    # df = spark ...
    df = spark.readStream.\
    format("kafka").\ # set data ingestion format as Kafka
    option("subscribe", b'service-calls').\ #This is required although it says option.
    option("kafka.bootstrap.servers", "localhost:9092").\ #You will also need the url and port of the bootstrap server
    option("startingOffsets", "earliest") .\
    option("maxOffsetsPerTrigger", 200). \
    load()
    
    # Show schema for the incoming resources for checks
    df.printSchema()

    # TODO extract the correct column from the kafka input resources
    # Take only value and convert it to String
    kafka_df = df.selectExpr("CAST(value as STRING)")

    service_table = kafka_df\
        .select(psf.from_json(psf.col('value'), schema).alias("SERVICE_CALLS"))\
        .select("SERVICE_CALLS.*")

    distinct_table = service_table\
        .select(psf.col('crime_id'),
                psf.col('original_crime_type_name'),
                psf.to_timestamp(psf.col('call_date_time')).alias('call_datetime'),
                psf.col('address'),
                psf.col('disposition'))

    # TODO get different types of original_crime_type_name in 60 minutes interval
    #counts_df = 

    # TODO use udf to convert timestamp to right format on a call_date_time column
    converted_df = distinct_table.withColumn("DateColconv", udf_convert_time('call_date_time'))

    # TODO apply aggregations using windows function to see how many calls occurred in 2 day span
    # calls_per_2_days =

    # TODO write output stream
    # query = 


    # TODO attach a ProgressReporter
    query.awaitTermination()


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    # TODO Create Spark in Local mode
    spark = SparkSession.builder.master("local").appName("CrimeDash").getOrCreate()

    logger.info("Spark started")

    run_spark_job(spark)

    spark.stop()



