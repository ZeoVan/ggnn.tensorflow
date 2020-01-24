DATA=sample_data
TRAIN_PATH=${DATA}/java-small-graph-transformed/training
VAL_PATH=${DATA}/java-small-graph-transformed/validation
BATCH_SIZE=20
VAL_BATCH_SIZE=3
DATA_THRESHOLD=100000
BUCKET_SIZE_THRESHOLD=1000
PYTHON=python3
${PYTHON} train_ggnn_method_name_prediction.py --train_path ${TRAIN_PATH} --val_path ${VAL_PATH} --batch_size ${BATCH_SIZE} --val_batch_size ${VAL_BATCH_SIZE} --data_threshold ${DATA_THRESHOLD} --bucket_size_threshold ${BUCKET_SIZE_THRESHOLD}
