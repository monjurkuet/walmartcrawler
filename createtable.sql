--
CREATE TABLE "productlist" (
    "Source_Link"    TEXT,
    "Title"    TEXT,
    "Original_Price"    TEXT,
    "Current_Price"    TEXT,
    "Product_Link"    TEXT UNIQUE,
    "Image_Link"    TEXT,
    "timestamp"    DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY("Product_Link")
);
