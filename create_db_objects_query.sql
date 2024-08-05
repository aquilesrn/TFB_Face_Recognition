CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE models (
    model_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT
);

CREATE TABLE images (
    image_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_path VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE analyses (
    analysis_id SERIAL PRIMARY KEY,
    image_id INTEGER NOT NULL,
    model_id INTEGER NOT NULL,
    analysis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    result_data JSON,
    FOREIGN KEY (image_id) REFERENCES images(image_id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES models(model_id) ON DELETE CASCADE
);

CREATE TABLE metrics (
    metric_id SERIAL PRIMARY KEY,
    analysis_id INTEGER NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    value VARCHAR(255) NOT NULL,
    FOREIGN KEY (analysis_id) REFERENCES analyses(analysis_id) ON DELETE CASCADE
);

CREATE INDEX idx_images_user_id ON images(user_id);
CREATE INDEX idx_analyses_image_id ON analyses(image_id);
CREATE INDEX idx_analyses_model_id ON analyses(model_id);
CREATE INDEX idx_metrics_analysis_id ON metrics(analysis_id);
