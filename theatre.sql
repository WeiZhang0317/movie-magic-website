DROP SCHEMA IF EXISTS theatre;
CREATE SCHEMA theatre;
USE theatre;

CREATE TABLE IF NOT EXISTS Genre (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS Rating (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Rating VARCHAR(50) NOT NULL
);


CREATE TABLE IF NOT EXISTS Actor (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS MovieReview (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    ReviewScore DECIMAL(2,1),
    NumberofRatings INT DEFAULT 1
);

CREATE TABLE IF NOT EXISTS Movie (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(255) NOT NULL,
    Language VARCHAR(50),
    Description TEXT,
    ReleaseDate Date,
    Image VARCHAR(255),
    Bigposter VARCHAR(255),
    Genre INT,
    Rating INT,
    Actor INT,
    Duration INT,
    MovieReview INT NULL,
    FOREIGN KEY (Genre) REFERENCES Genre(ID),
    FOREIGN KEY (Rating) REFERENCES Rating(ID),
    FOREIGN KEY (Actor) REFERENCES Actor(ID),
    FOREIGN KEY (MovieReview) REFERENCES MovieReview(ID)
);

CREATE TABLE IF NOT EXISTS User (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  Email VARCHAR(255) UNIQUE NOT NULL,
  Password VARCHAR(255) NOT NULL,
  Role ENUM('Customer', 'Staff', 'Manager', 'Admin') NOT NULL,
  IsActive BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS Customer(
    ID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT UNIQUE,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Email VARCHAR(255) NOT NULL,
    Mobile VARCHAR(20),
    DateOfBirth DATE,
    IsActive BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (UserID) REFERENCES User(ID)
);

CREATE TABLE IF NOT EXISTS Staff(
    ID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT UNIQUE,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Email VARCHAR(255) NOT NULL,
    Mobile VARCHAR(20),
    IsActive BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (UserID) REFERENCES User(ID)
);

CREATE TABLE IF NOT EXISTS Manager(
    ID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT UNIQUE,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Email VARCHAR(255) NOT NULL,
    Mobile VARCHAR(20),
    IsActive BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (UserID) REFERENCES User(ID)
);

CREATE TABLE IF NOT EXISTS Admin(
    ID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT UNIQUE,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Email VARCHAR(255) NOT NULL,
    Mobile VARCHAR(20),
    IsActive BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (UserID) REFERENCES User(ID)
);


CREATE TABLE IF NOT EXISTS Cinema (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  Name VARCHAR(255) UNIQUE NOT NULL,
  Capacity INT NOT NULL,
  CinemaImage VARCHAR(255)
);


CREATE TABLE IF NOT EXISTS Session (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  Movie INT NOT NULL,
  Cinema INT NOT NULL,
  Date DATE NOT NULL,
  DayOfWeek ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'), 
  StartTime TIME NOT NULL,
  FOREIGN KEY (Movie) REFERENCES Movie(ID),
  FOREIGN KEY (Cinema) REFERENCES Cinema(ID)
);

CREATE TABLE IF NOT EXISTS Seat (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  RowNumber INT NOT NULL,
  SeatNumber INT NOT NULL,
  Cinema INT NOT NULL,
  FOREIGN KEY (Cinema) REFERENCES Cinema(ID)
);

CREATE TABLE IF NOT EXISTS SessionSeat (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  Session INT NOT NULL,
  Seat INT NOT NULL,
  Available BOOLEAN NOT NULL DEFAULT TRUE,
  FOREIGN KEY (Session) REFERENCES Session(ID),
  FOREIGN KEY (Seat) REFERENCES Seat(ID)
);

CREATE TABLE WeeklyDiscounts (
	ID INT AUTO_INCREMENT PRIMARY KEY,
    DayOfWeek ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
    DiscountPercent DECIMAL(5,2) NOT NULL CHECK (DiscountPercent >= 0 AND DiscountPercent <= 100),
    DiscountImage VARCHAR(255),
    Title TEXT,
	Description TEXT
);
    

CREATE TABLE IF NOT EXISTS GiftCard(
  ID INT AUTO_INCREMENT PRIMARY KEY,
  Number VARCHAR(20) NOT NULL UNIQUE,
  Email VARCHAR(255) NOT NULL,
  Balance DECIMAL(10, 2),
  Type ENUM('25', '50', '100') NOT NULL,
  ImgPath VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS Coupon(
  ID INT AUTO_INCREMENT PRIMARY KEY,
  Code VARCHAR(20) NOT NULL UNIQUE,
  Discount DECIMAL(10, 2),
  CouponImage VARCHAR(255),
  Title TEXT,
  Description TEXT
);

CREATE TABLE UserCouponUsage (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    User INT,
    Coupon INT,
    FOREIGN KEY (User) REFERENCES User(ID),
    FOREIGN KEY (Coupon) REFERENCES Coupon(ID)
);

CREATE TABLE IF NOT EXISTS Booking (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  User INT NOT NULL,
  Session INT NOT NULL,
  CreatedTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  Status ENUM('pending', 'paid', 'canceled') DEFAULT 'pending',
  FOREIGN KEY (User) REFERENCES User(ID),
  FOREIGN KEY (Session) REFERENCES Session(ID)
);

CREATE TABLE IF NOT EXISTS Payment (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    BookingID INT,
    PaymentTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PaymentMethod ENUM('creditCard', 'internetBanking', 'giftCard'),
    TotalAmount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (BookingID) REFERENCES Booking(ID) 
);

CREATE TABLE IF NOT EXISTS TicketType (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  TypeName ENUM('Children', 'Student', 'Adult', 'Senior') NOT NULL UNIQUE,
  Price DECIMAL(10, 2) NOT NULL
);


CREATE TABLE IF NOT EXISTS Ticket (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  Booking INT NOT NULL,
  SessionSeat INT NOT NULL,
  TicketType INT NOT NULL,  
  Checkin BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (Booking) REFERENCES Booking(ID),
  FOREIGN KEY (SessionSeat) REFERENCES SessionSeat(ID),
  FOREIGN KEY (TicketType) REFERENCES TicketType(ID)
);



CREATE TABLE IF NOT EXISTS FoodCombo (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  Name VARCHAR(50) NOT NULL,
  Price DECIMAL(10, 2) NOT NULL,
  Image VARCHAR(255) NOT NULL,
  Description VARCHAR(255) 
);

CREATE TABLE IF NOT EXISTS BookingFoodCombo (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  BookingID INT,
  FoodComboID INT,
  FOREIGN KEY (BookingID) REFERENCES Booking(ID),
  FOREIGN KEY (FoodComboID) REFERENCES FoodCombo(ID)
);

-- Insert Combos
INSERT INTO FoodCombo (Name, Price, Image, Description) VALUES ('Combo#1', 11.00, 'combo_1.jpg', 'L&P X1, Crispy Chips X1');
INSERT INTO FoodCombo (Name, Price, Image, Description) VALUES ('Combo#2', 12.00, 'combo_2.jpg', 'CocaCola X1, Popcorn X1');
INSERT INTO FoodCombo (Name, Price, Image, Description) VALUES ('Combo#3', 15.00, 'combo_3.jpg', 'Milkshake X1, Cookie X1');
INSERT INTO FoodCombo (Name, Price, Image, Description) VALUES ('Crispy Chips', 6.00, 'chips.jpg', 'Crispy Chips X1');
INSERT INTO FoodCombo (Name, Price, Image, Description) VALUES ('Popcorn', 7.00, 'popcorn.jpg', 'Popcorn X1');
INSERT INTO FoodCombo (Name, Price, Image, Description) VALUES ('Cookie', 5.00, 'cookie.jpg', 'Cookie X1');
INSERT INTO FoodCombo (Name, Price, Image, Description) VALUES ('L&P', 6.00, 'l&p.jpg', 'L&P X1');
INSERT INTO FoodCombo (Name, Price, Image, Description) VALUES ('Coke', 6.00, 'coke.jpg', 'CocaCola X1');
INSERT INTO FoodCombo (Name, Price, Image, Description) VALUES ('Milkshake', 11.00, 'milkshake.jpg', 'Milkshake X1');



-- Insert ratings
INSERT INTO Rating (Rating) VALUES ('PG');
INSERT INTO Rating (Rating) VALUES ('M');
INSERT INTO Rating (Rating) VALUES ('R');
INSERT INTO Rating (Rating) VALUES ('NC-17');

-- Insert reviews
INSERT INTO MovieReview (ReviewScore) VALUES (6.0);
INSERT INTO MovieReview (ReviewScore) VALUES (6.5);
INSERT INTO MovieReview (ReviewScore) VALUES (7.0);
INSERT INTO MovieReview (ReviewScore) VALUES (7.5);
INSERT INTO MovieReview (ReviewScore) VALUES (8.0);
INSERT INTO MovieReview (ReviewScore) VALUES (9.0);



-- Insert genres
INSERT INTO Genre (Name) VALUES ('Action');
INSERT INTO Genre (Name) VALUES ('Drama');
INSERT INTO Genre (Name) VALUES ('Sci-Fi');
INSERT INTO Genre (Name) VALUES ('Comedy');
INSERT INTO Genre (Name) VALUES ('Romance');

-- Insert additional actors
INSERT INTO Actor (Name) 
VALUES 
('Leonardo DiCaprio, Kate Winslet, Tom Hardy, Scarlett Johansson, Emma Watson'),
('Brad Pitt, Angelina Jolie, George Clooney, Julia Roberts, Charlize Theron'),
('Meryl Streep, Robert De Niro, Cate Blanchett, Morgan Freeman, Nicole Kidman'),
('Tom Hanks, Sandra Bullock, Johnny Depp, Natalie Portman, Denzel Washington'),
('Emma Stone, Ryan Gosling, Bradley Cooper, Jennifer Lawrence, Chris Hemsworth'),
('Joaquin Phoenix, Charlize Theron, Morgan Freeman, Kate Winslet, Tom Hanks'),
('Scarlett Johansson, Brad Pitt, Nicole Kidman, Robert Downey Jr., Cate Blanchett'),
('Chris Evans, Angelina Jolie, Denzel Washington, Julia Roberts, Johnny Depp');


-- Insert additional movies
INSERT INTO Movie (Title, Language, Description, ReleaseDate, Image, Genre, Rating, Actor, Duration, MovieReview) 
VALUES 
('Inception', 'English', 'A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a CEO.','2024-01-10', 'inception.jpg', 1, 1,1, 150,1),
('Fight Club', 'English', 'An insomniac office worker and a devil-may-care soapmaker form an underground fight club that evolves into something much more.', '2024-01-11', 'fightclub.jpg', 2, 2, 2, 139,2),
('The Post', 'English', 'A cover-up that spanned four U.S. Presidents pushed the country first female newspaper publisher and a hard-driving editor to join an unprecedented battle between the press and the government.', '2024-01-12','thepost.jpg', 3, 1, 3, 120,3),
('Forrest Gump', 'English', 'The presidencies of Kennedy and Johnson, the Vietnam War, the Watergate scandal and other historical events unfold from the perspective of an Alabama man with an IQ of 75.', '2024-01-01', 'forrestgump.jpg', 1, 2, 4, 142,4),
('The Iron Lady', 'English', 'An elderly Margaret Thatcher talks to the imagined presence of her recently deceased husband as she struggles to come to terms with his death while scenes from her past life, from girlhood to British prime minister, intervene.', '2024-01-07','ironlady.jpg', 3, 1, 3,105,5),
('Cast Away', 'English', 'A FedEx executive undergoes a physical and emotional transformation after crash landing on a deserted island.', '2023-11-30','castaway.jpg', 1, 2, 4,143,6),
('The Aviator', 'Japanese', 'A biopic depicting the early years of legendary Director and aviator Howard Hughes\' career from the late 1920s to the mid 1940s.', '2024-03-03','aviator.jpg', 2, 1, 1,169,NULL),
('La La Land', 'French', 'A jazz pianist falls for an aspiring actress in Los Angeles.','2024-03-07',  'lalaland.jpg',5, 2, 5,128,NULL),
('Blade Runner 2049', 'English', 'A young blade runner\'s discovery of a long-buried secret leads him to track down former blade runner Rick Deckard, who\'s been missing for thirty years.', '2024-03-17', 'bladerunner2049.jpg',3, 3, 6, 163,NULL),
('The Hunger Games', 'English', 'Katniss Everdeen voluntarily takes her younger sister\'s place in the Hunger Games: a televised competition in which two teenagers from each of the twelve Districts of Panem are chosen at random to fight to the death.', '2024-03-12', 'hungergames.jpg', 4, 3, 7, 142,NULL),
('Thor: Ragnarok', 'English', 'Imprisoned on the planet Sakaar, Thor must race against time to return to Asgard and stop Ragnarök, the destruction of his world, at the hands of the powerful and ruthless villain Hela.', '2024-04-01', 'thorragnarok.jpg', 4, 4, 8,130,NULL);

-- Update the Bigposter for 'Inception'
UPDATE Movie
SET Bigposter = 'inception_bigposter.jpg'
WHERE Title = 'Inception' AND ID = 1;

-- Update the Bigposter for 'Ironlady'
UPDATE Movie
SET Bigposter = 'ironlady_bigposter.jpg'
WHERE Title = 'The Iron Lady'AND ID=5;

-- Update the Bigposter for 'forrestgump'
UPDATE Movie
SET Bigposter = 'forrestgump_bigposter.png'
WHERE Title = 'Forrest Gump'AND ID=4;


INSERT INTO Cinema (Name, Capacity, CinemaImage) VALUES
('Starlight Cinema', 48, 'starlight.jpg'),
('Moonlight Cinema', 48, 'moonlight.jpg'),
('Galaxy Cinema', 48, 'galaxy.jpg'),
('Widescreen Cinema', 300, 'widescreen.jpg');

INSERT INTO WeeklyDiscounts (DayOfWeek, DiscountPercent, DiscountImage, Title, Description) VALUES
('Tuesday', 50.00, 'tuesday_sale.jpg', 'Tuesday Daytime Sale', 'Enjoy a magical movie experience every Tuesday! Take advantage of our Tuesday Movie Discount with 50% off all Tuesday Daytime session movies. Your perfect opportunity to catch the latest films at half the price. Do not miss out on this amazing deal at Movie Magic Theatre!'),
('Friday', 20.00, 'happy_friday_sale.jpg', 'Happy Friday Sale', 'Every Friday, enjoy a special 20% discount on all movies. Immerse yourself in the magic of the silver screen with friends and family, and take advantage of this irresistible offer! ');

INSERT INTO Coupon (Code, Discount,CouponImage, Title, Description) VALUES
("NEWUSER5", 5.00, 'new_customer_special.jpg','New Customer Special','Welcome to Movie Magic! Use the code NEWUSER5 at checkout to get $5.00 OFF on your first purchase. Enjoy your movie with a special discount just for you!');

INSERT INTO User (Email, Password, Role) VALUES 
('sophie.wilson@gmail.com', '$2b$12$KJAcUy1Gt8B3M6fomjFj7.grko0nYUkNI07mqBu6abjhv/i3qF1bG', 'Staff'),
('james.taylor@gmail.com', '$2b$12$qi02wN43K8.hdSaqltMwUO6i5r7AUd5vA9TAO8hFytmVk71UogXvW','Staff'),
('emma.patel@gmail.com', '$2b$12$S3jMEX1I/WUziJaQ51906e/rZ3JRlWZkuGVljSC6QRGbmMK25Ew76','Staff'),
('liam.chen@gmail.com', '$2b$12$yo1ztIw6ZAeEVtr5M0CCx.z5mUA0QsokNNDQq.AH5P/QZ7sbh25M6','Staff'),
('olivia.smith@gmail.com', '$2b$12$1eJgjJ7RHeRm4hqp9/8Csei0nyaRDicAwBc9Fvwb/qVo8k4N708DG','Staff'),
('daniel.robinson@gmail.com', '$2b$12$PCXLd0MGxJAW6lhlpf.UnOOLCPxs4d6Wbcv2BA2uQJczIE1Zs0nQC','Manager'),
('charlotte.brown@gmail.com', '$2b$12$sorNiW3YUeWFgiPW40h0suZY8MJOGjfvGv8eyS9KGVL5jYElFdn..','Admin'),
('michael.johnson@gmail.com', '$2b$12$teQt1dN5bKQPKg.wSVpbGO2PghCJVf95ENb3oEj2R2ijzfWglTy0C', 'Customer'),
('sophia.kim@gmail.com', '$2b$12$GkztnU0vKqNYl0/uxBOgoORM2niy8xbWgPgUaYGUPvBqTKGQroe3m', 'Customer');

INSERT INTO Staff (UserID, FirstName, LastName, Email, Mobile) VALUES 
(1,'Sophie', 'Wilson', 'sophie.wilson@gmail.com', '021 123 4567'),
(2,'James', 'Taylor', 'james.taylor@gmail.com', '022 234 5678'),
(3,'Emma', 'Patel', 'emma.patel@gmail.com', '027 345 6789'),
(4,'Liam', 'Chen', 'liam.chen@gmail.com', '025 456 7890'),
(5,'Olivia', 'Smith', 'olivia.smith@gmail.com', '029 567 8901');

INSERT INTO Manager (UserID, FirstName, LastName, Email, Mobile) VALUES 
(6, 'Daniel', 'Robinson', 'daniel.robinson@gmail.com', '021 987 6543');

INSERT INTO Admin (UserID, FirstName, LastName, Email, Mobile) VALUES 
(7, 'Charlotte', 'Brown', 'charlotte.brown@gmail.com', '021 765 4321');

INSERT INTO Customer (UserID, FirstName, LastName, Email, Mobile) VALUES 
(8, 'Michael', 'Johnson', 'michael.johnson@gmail.com', '020 678 9012'),
(9, 'Sophia', 'Kim', 'sophia.kim@gmail.com', '021 789 0123');


-- Inserting data into the Session table
INSERT INTO Session (Movie, Cinema, Date, DayOfWeek, StartTime) VALUES
(1, 1, '2024-01-04', 'Thursday', '15:00'),
(1, 4, '2024-02-09', 'Friday', '20:00'),
(1, 3, '2024-02-09', 'Friday', '14:00'),
(1, 3, '2024-02-12', 'Monday', '09:00'),
(1, 1, '2024-02-12', 'Monday', '15:00'),
(1, 2, '2024-02-12', 'Monday', '20:00'),
(1, 2, '2024-02-13', 'Tuesday', '14:00'),
(1, 2, '2024-02-14', 'Wednesday', '14:00'),
(1, 1, '2024-02-15', 'Thursday', '21:00'),
(1, 3, '2024-02-16', 'Friday', '21:00'),
(1, 4, '2024-02-17', 'Saturday', '21:00'),
(1, 1, '2024-02-18', 'Sunday', '20:00'),
(1, 3, '2024-02-19', 'Monday', '18:30'),
(1, 1, '2024-02-20', 'Tuesday', '14:00'),
(1, 2, '2024-02-20', 'Tuesday', '20:00'),

(2, 1, '2024-01-14', 'Sunday', '15:00'),
(2, 2, '2024-01-23', 'Tuesday', '17:00'),
(2, 4, '2024-02-12', 'Monday', '18:30'),
(2, 1, '2024-02-14', 'Wednesday', '15:00'),
(2, 1, '2024-02-16', 'Friday', '19:30'),
(2, 1, '2024-02-17', 'Saturday', '14:00'),
(2, 2, '2024-02-23', 'Friday', '17:00'),

(3, 2, '2024-01-16', 'Tuesday', '18:00'),
(3, 1, '2024-01-25', 'Thursday', '15:30'),
(3, 3, '2024-02-07', 'Wednesday', '14:00'),
(3, 1, '2024-02-13', 'Tuesday', '20:00'),
(3, 2, '2024-02-16', 'Friday', '18:00'),
(3, 4, '2024-02-16', 'Friday', '17:00'),
(3, 1, '2024-02-25', 'Sunday', '15:30'),

(4, 3, '2024-01-18', 'Thursday', '14:30'),
(4, 2, '2024-02-08', 'Thursday', '19:00'),
(4, 4, '2024-02-12', 'Monday', '16:00'),
(4, 2, '2024-02-13', 'Tuesday', '15:30'),
(4, 2, '2024-02-14', 'Wednesday', '17:00'),
(4, 1, '2024-02-15', 'Thursday', '18:00'),
(4, 2, '2024-02-17', 'Saturday', '19:30'),
(4, 3, '2024-02-18', 'Sunday', '14:30'),
(4, 2, '2024-02-20', 'Tuesday', '10:00'),

(5, 1, '2024-01-10', 'Wednesday', '16:30'),
(5, 4, '2024-01-19', 'Friday', '19:30'),
(5, 1, '2024-02-10', 'Saturday', '16:30'),
(5, 2, '2024-02-14', 'Wednesday', '19:30'),
(5, 3, '2024-02-14', 'Wednesday', '16:00'),
(5, 4, '2024-02-19', 'Monday', '19:30'),

(6, 4, '2024-01-11', 'Thursday', '17:30'),
(6, 1, '2024-01-21', 'Sunday', '16:00'),
(6, 3, '2024-02-10', 'Saturday', '16:30'),
(6, 1, '2024-02-15', 'Thursday', '15:30'),
(6, 4, '2024-02-18', 'Sunday', '17:30'),
(6, 1, '2024-02-19', 'Monday', '15:00'),
(6, 1, '2024-02-21', 'Wednesday', '16:00');


-- Inserting data into the Seat table
INSERT INTO Seat (RowNumber, SeatNumber, Cinema)
VALUES
(1, 1, 1),
(1, 2, 1),
(1, 3, 1),
(1, 4, 1),
(1, 5, 1),
(1, 6, 1),
(1, 7, 1),
(1, 8, 1),

(2, 1, 1),
(2, 2, 1),
(2, 3, 1),
(2, 4, 1),
(2, 5, 1),
(2, 6, 1),
(2, 7, 1),
(2, 8, 1),

(3, 1, 1),
(3, 2, 1),
(3, 3, 1),
(3, 4, 1),
(3, 5, 1),
(3, 6, 1),
(3, 7, 1),
(3, 8, 1),

(4, 1, 1),
(4, 2, 1),
(4, 3, 1),
(4, 4, 1),
(4, 5, 1),
(4, 6, 1),
(4, 7, 1),
(4, 8, 1),

(5, 1, 1),
(5, 2, 1),
(5, 3, 1),
(5, 4, 1),
(5, 5, 1),
(5, 6, 1),
(5, 7, 1),
(5, 8, 1),

(6, 1, 1),
(6, 2, 1),
(6, 3, 1),
(6, 4, 1),
(6, 5, 1),
(6, 6, 1),
(6, 7, 1),
(6, 8, 1),

(1, 1, 2),
(1, 2, 2),
(1, 3, 2),
(1, 4, 2),
(1, 5, 2),
(1, 6, 2),
(1, 7, 2),
(1, 8, 2),

(2, 1, 2),
(2, 2, 2),
(2, 3, 2),
(2, 4, 2),
(2, 5, 2),
(2, 6, 2),
(2, 7, 2),
(2, 8, 2),

(3, 1, 2),
(3, 2, 2),
(3, 3, 2),
(3, 4, 2),
(3, 5, 2),
(3, 6, 2),
(3, 7, 2),
(3, 8, 2),

(4, 1, 2),
(4, 2, 2),
(4, 3, 2),
(4, 4, 2),
(4, 5, 2),
(4, 6, 2),
(4, 7, 2),
(4, 8, 2),

(5, 1, 2),
(5, 2, 2),
(5, 3, 2),
(5, 4, 2),
(5, 5, 2),
(5, 6, 2),
(5, 7, 2),
(5, 8, 2),

(6, 1, 2),
(6, 2, 2),
(6, 3, 2),
(6, 4, 2),
(6, 5, 2),
(6, 6, 2),
(6, 7, 2),
(6, 8, 2),

(1, 1, 3),
(1, 2, 3),
(1, 3, 3),
(1, 4, 3),
(1, 5, 3),
(1, 6, 3),
(1, 7, 3),
(1, 8, 3),

(2, 1, 3),
(2, 2, 3),
(2, 3, 3),
(2, 4, 3),
(2, 5, 3),
(2, 6, 3),
(2, 7, 3),
(2, 8, 3),

(3, 1, 3),
(3, 2, 3),
(3, 3, 3),
(3, 4, 3),
(3, 5, 3),
(3, 6, 3),
(3, 7, 3),
(3, 8, 3),

(4, 1, 3),
(4, 2, 3),
(4, 3, 3),
(4, 4, 3),
(4, 5, 3),
(4, 6, 3),
(4, 7, 3),
(4, 8, 3),

(5, 1, 3),
(5, 2, 3),
(5, 3, 3),
(5, 4, 3),
(5, 5, 3),
(5, 6, 3),
(5, 7, 3),
(5, 8, 3),

(6, 1, 3),
(6, 2, 3),
(6, 3, 3),
(6, 4, 3),
(6, 5, 3),
(6, 6, 3),
(6, 7, 3),
(6, 8, 3);

INSERT INTO Seat (RowNumber, SeatNumber, Cinema)
VALUES
(1, 1, 4), (1, 2, 4), (1, 3, 4), (1, 4, 4), (1, 5, 4), (1, 6, 4), (1, 7, 4), (1, 8, 4), (1, 9, 4), (1, 10, 4),
(1, 11, 4), (1, 12, 4), (1, 13, 4), (1, 14, 4), (1, 15, 4), (1, 16, 4), (1, 17, 4), (1, 18, 4), (1, 19, 4), (1, 20, 4),
(1, 21, 4), (1, 22, 4), (1, 23, 4), (1, 24, 4), (1, 25, 4),
(2, 1, 4), (2, 2, 4), (2, 3, 4), (2, 4, 4), (2, 5, 4), (2, 6, 4), (2, 7, 4), (2, 8, 4), (2, 9, 4), (2, 10, 4),
(2, 11, 4), (2, 12, 4), (2, 13, 4), (2, 14, 4), (2, 15, 4), (2, 16, 4), (2, 17, 4), (2, 18, 4), (2, 19, 4), (2, 20, 4),
(2, 21, 4), (2, 22, 4), (2, 23, 4), (2, 24, 4), (2, 25, 4),
(3, 1, 4), (3, 2, 4), (3, 3, 4), (3, 4, 4), (3, 5, 4), (3, 6, 4), (3, 7, 4), (3, 8, 4), (3, 9, 4), (3, 10, 4),
(3, 11, 4), (3, 12, 4), (3, 13, 4), (3, 14, 4), (3, 15, 4), (3, 16, 4), (3, 17, 4), (3, 18, 4), (3, 19, 4), (3, 20, 4),
(3, 21, 4), (3, 22, 4), (3, 23, 4), (3, 24, 4), (3, 25, 4),
(4, 1, 4), (4, 2, 4), (4, 3, 4), (4, 4, 4), (4, 5, 4), (4, 6, 4), (4, 7, 4), (4, 8, 4), (4, 9, 4), (4, 10, 4),
(4, 11, 4), (4, 12, 4), (4, 13, 4), (4, 14, 4), (4, 15, 4), (4, 16, 4), (4, 17, 4), (4, 18, 4), (4, 19, 4), (4, 20, 4),
(4, 21, 4), (4, 22, 4), (4, 23, 4), (4, 24, 4), (4, 25, 4),
(5, 1, 4), (5, 2, 4), (5, 3, 4), (5, 4, 4), (5, 5, 4), (5, 6, 4), (5, 7, 4), (5, 8, 4), (5, 9, 4), (5, 10, 4),
(5, 11, 4), (5, 12, 4), (5, 13, 4), (5, 14, 4), (5, 15, 4), (5, 16, 4), (5, 17, 4), (5, 18, 4), (5, 19, 4), (5, 20, 4),
(5, 21, 4), (5, 22, 4), (5, 23, 4), (5, 24, 4), (5, 25, 4),
(6, 1, 4), (6, 2, 4), (6, 3, 4), (6, 4, 4), (6, 5, 4), (6, 6, 4), (6, 7, 4), (6, 8, 4), (6, 9, 4), (6, 10, 4),
(6, 11, 4), (6, 12, 4), (6, 13, 4), (6, 14, 4), (6, 15, 4), (6, 16, 4), (6, 17, 4), (6, 18, 4), (6, 19, 4), (6, 20, 4),
(6, 21, 4), (6, 22, 4), (6, 23, 4), (6, 24, 4), (6, 25, 4),
(7, 1, 4), (7, 2, 4), (7, 3, 4), (7, 4, 4), (7, 5, 4), (7, 6, 4), (7, 7, 4), (7, 8, 4), (7, 9, 4), (7, 10, 4),
(7, 11, 4), (7, 12, 4), (7, 13, 4), (7, 14, 4), (7, 15, 4), (7, 16, 4), (7, 17, 4), (7, 18, 4), (7, 19, 4), (7, 20, 4),
(7, 21, 4), (7, 22, 4), (7, 23, 4), (7, 24, 4), (7, 25, 4),
(8, 1, 4), (8, 2, 4), (8, 3, 4), (8, 4, 4), (8, 5, 4), (8, 6, 4), (8, 7, 4), (8, 8, 4), (8, 9, 4), (8, 10, 4),
(8, 11, 4), (8, 12, 4), (8, 13, 4), (8, 14, 4), (8, 15, 4), (8, 16, 4), (8, 17, 4), (8, 18, 4), (8, 19, 4), (8, 20, 4),
(8, 21, 4), (8, 22, 4), (8, 23, 4), (8, 24, 4), (8, 25, 4),
(9, 1, 4), (9, 2, 4), (9, 3, 4), (9, 4, 4), (9, 5, 4), (9, 6, 4), (9, 7, 4), (9, 8, 4), (9, 9, 4), (9, 10, 4),
(9, 11, 4), (9, 12, 4), (9, 13, 4), (9, 14, 4), (9, 15, 4), (9, 16, 4), (9, 17, 4), (9, 18, 4), (9, 19, 4), (9, 20, 4),
(9, 21, 4), (9, 22, 4), (9, 23, 4), (9, 24, 4), (9, 25, 4),
(10, 1, 4), (10, 2, 4), (10, 3, 4), (10, 4, 4), (10, 5, 4), (10, 6, 4), (10, 7, 4), (10, 8, 4), (10, 9, 4), (10, 10, 4),
(10, 11, 4), (10, 12, 4), (10, 13, 4), (10, 14, 4), (10, 15, 4), (10, 16, 4), (10, 17, 4), (10, 18, 4), (10, 19, 4), (10, 20, 4),
(10, 21, 4), (10, 22, 4), (10, 23, 4), (10, 24, 4), (10, 25, 4),
(11, 1, 4), (11, 2, 4), (11, 3, 4), (11, 4, 4), (11, 5, 4), (11, 6, 4), (11, 7, 4), (11, 8, 4), (11, 9, 4), (11, 10, 4),
(11, 11, 4), (11, 12, 4), (11, 13, 4), (11, 14, 4), (11, 15, 4), (11, 16, 4), (11, 17, 4), (11, 18, 4), (11, 19, 4), (11, 20, 4),
(11, 21, 4), (11, 22, 4), (11, 23, 4), (11, 24, 4), (11, 25, 4),
(12, 1, 4), (12, 2, 4), (12, 3, 4), (12, 4, 4), (12, 5, 4), (12, 6, 4), (12, 7, 4), (12, 8, 4), (12, 9, 4), (12, 10, 4),
(12, 11, 4), (12, 12, 4), (12, 13, 4), (12, 14, 4), (12, 15, 4), (12, 16, 4), (12, 17, 4), (12, 18, 4), (12, 19, 4), (12, 20, 4),
(12, 21, 4), (12, 22, 4), (12, 23, 4), (12, 24, 4), (12, 25, 4);

-- Inserting data into the SessionSeat table
INSERT INTO SessionSeat (Session, Seat)
SELECT
    S.ID AS Session,
    St.ID AS Seat
FROM
    Session S
CROSS JOIN
    Seat St;


INSERT INTO TicketType (TypeName, Price) VALUES
('Children', 10.00),
('Student', 15.00),
('Adult', 20.00),
('Senior', 18.00);

INSERT INTO Booking (User, Session, CreatedTime, Status) 
VALUES 
(9, 2, '2024-01-20 17:19:42','paid'),
(9, 3, '2024-01-20 17:33:49','paid'),
(9, 1, '2024-01-01 17:42:35', 'paid'),
(9, 16, '2024-01-10 18:59:22', 'paid'),
(9, 39, '2024-01-07 19:03:14', 'paid'),
(9, 45, '2024-01-08 19:24:15', 'paid'),
(9, 31, '2024-02-01 19:35:30', 'paid'),
(9, 25, '2024-02-02 19:38:31', 'paid'),
(8, 41, '2024-02-03 19:43:25', 'paid'),
(8, 25, '2024-02-04 19:46:32', 'paid'),
(8, 16, '2024-02-04 19:52:58', 'paid'),
(8, 41, '2024-02-04 19:58:49', 'paid');



INSERT INTO Ticket (Booking, SessionSeat, TicketType) 
VALUES
(1,21521,3),
(1,21572,3),
(1,21623,3),
(2,6169,2),
(2,6220,2),
(2,6271,4),
(2,6322,4),
(3,2346,1),
(4,2178,3),
(5, 2155, 3),
(6, 22549, 3),
(6, 22600, 3),
(7, 4611, 3),
(8, 6912, 3),
(8, 6861, 3),
(9, 2153, 4),
(9, 2204, 4),
(10, 7269, 2),
(11, 2229, 1),
(11, 2280, 3),
(11, 2331, 3),
(11, 2433, 3),
(12, 1133, 3),
(12, 1082, 3),
(12, 1184, 3);

UPDATE SessionSeat
SET Available = 0
WHERE ID IN (SELECT SessionSeat FROM Ticket);


INSERT INTO Payment (BookingID, PaymentTime, PaymentMethod, TotalAmount) VALUES
(1, '2024-01-20 17:19:42', 'internetBanking', 48.00),
(2, '2024-01-20 17:34:06', 'internetBanking', 52.80),
(3, '2024-01-01 17:42:48', 'creditCard', 30.00),
(4, '2024-01-10 18:59:31', 'internetBanking', 20.00),
(5, '2024-01-07 19:03:32', 'creditCard', 20.00),
(6, '2024-01-08 19:24:23', 'giftCard', 40.00),
(7, '2024-02-01 19:36:19', 'creditCard', 65.00),
(8, '2024-02-02 19:38:47', 'creditCard', 40.00),
(9, '2024-02-03 19:43:47', 'creditCard', 36.00),
(10, '2024-02-04 19:46:46', 'internetBanking', 21.00),
(11, '2024-02-04 19:53:19', 'creditCard', 127.00),
(12, '2024-02-04 19:59:25', 'creditCard', 93.00);


