CREATE TABLE [productdetails] ( 
  [productid] INT NULL,
  [Category] VARCHAR(250) NULL,
  [UPC] VARCHAR(250) NULL,
  [updatedat] DATETIME NULL DEFAULT CURRENT_TIMESTAMP ,
   PRIMARY KEY ([productid])
);
CREATE TABLE [productlist] ( 
  [Source_Link] TEXT NULL,
  [Title] TEXT NULL,
  [Original_Price] TEXT NULL,
  [Current_Price] TEXT NULL,
  [Product_Link] TEXT NULL,
  [Image_Link] TEXT NULL,
  [timestamp] DATETIME NULL DEFAULT CURRENT_TIMESTAMP ,
  [productid] INT NULL,
   PRIMARY KEY ([productid])
);
CREATE VIEW 'productdetails+productlist' as
SELECT * FROM productlist LEFT JOIN productdetails ON
productlist.productid=productdetails.productid
WHERE productdetails.productid IS NOT NULL;
