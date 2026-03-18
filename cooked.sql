/*
 Navicat Premium Data Transfer

 Source Server         : root
 Source Server Type    : MySQL
 Source Server Version : 80041 (8.0.41)
 Source Host           : localhost:3306
 Source Schema         : recipeboxd

 Target Server Type    : MySQL
 Target Server Version : 80041 (8.0.41)
 File Encoding         : 65001

 Date: 09/03/2026 22:51:18
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for countries
-- ----------------------------
DROP TABLE IF EXISTS `countries`;
CREATE TABLE `countries`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `map_code` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uq_countries_name`(`name` ASC) USING BTREE,
  INDEX `ix_countries_name`(`name` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 10 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of countries
-- ----------------------------
INSERT INTO `countries` VALUES (1, 'United Kingdom', 'GB');
INSERT INTO `countries` VALUES (2, 'United States', 'US');
INSERT INTO `countries` VALUES (3, 'France', 'FR');
INSERT INTO `countries` VALUES (4, 'Italy', 'IT');
INSERT INTO `countries` VALUES (5, 'China', 'CN');
INSERT INTO `countries` VALUES (6, 'Japan', 'JP');
INSERT INTO `countries` VALUES (7, 'India', 'IN');
INSERT INTO `countries` VALUES (8, 'Mexico', 'MX');
INSERT INTO `countries` VALUES (9, 'Thailand', 'TH');

-- ----------------------------
-- Table structure for follows
-- ----------------------------
DROP TABLE IF EXISTS `follows`;
CREATE TABLE `follows`  (
  `follower_id` int NOT NULL,
  `followed_id` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`follower_id`, `followed_id`) USING BTREE,
  INDEX `fk_follows_followed`(`followed_id` ASC) USING BTREE,
  CONSTRAINT `fk_follows_followed` FOREIGN KEY (`followed_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_follows_follower` FOREIGN KEY (`follower_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of follows
-- ----------------------------
INSERT INTO `follows` VALUES (1, 3, '2026-03-06 16:50:07');

-- ----------------------------
-- Table structure for ingredients
-- ----------------------------
DROP TABLE IF EXISTS `ingredients`;
CREATE TABLE `ingredients`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `category` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'General',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uq_ingredients_name`(`name` ASC) USING BTREE,
  INDEX `ix_ingredients_name`(`name` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 18 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of ingredients
-- ----------------------------
INSERT INTO `ingredients` VALUES (1, '鸡蛋', '蛋奶');
INSERT INTO `ingredients` VALUES (2, '牛奶', '蛋奶');
INSERT INTO `ingredients` VALUES (3, '黄油', '调味');
INSERT INTO `ingredients` VALUES (4, '面粉', '烘焙');
INSERT INTO `ingredients` VALUES (5, '西红柿', '蔬菜');
INSERT INTO `ingredients` VALUES (6, '洋葱', '蔬菜');
INSERT INTO `ingredients` VALUES (7, '大蒜', '蔬菜');
INSERT INTO `ingredients` VALUES (8, '黑胡椒', '调味');
INSERT INTO `ingredients` VALUES (9, '盐', '调味');
INSERT INTO `ingredients` VALUES (10, '橄榄油', '调味');
INSERT INTO `ingredients` VALUES (11, '意大利面', '主食');
INSERT INTO `ingredients` VALUES (12, '牛腩', '肉类');
INSERT INTO `ingredients` VALUES (13, '米饭', '主食');
INSERT INTO `ingredients` VALUES (14, '鸡腿', '肉类');
INSERT INTO `ingredients` VALUES (15, '酱油', '调味');
INSERT INTO `ingredients` VALUES (16, '蜂蜜', '调味');
INSERT INTO `ingredients` VALUES (17, '柠檬', '水果');

-- ----------------------------
-- Table structure for photos
-- ----------------------------
DROP TABLE IF EXISTS `photos`;
CREATE TABLE `photos`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `image_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `caption` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `upload_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `recipe_id` int NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_photos_user_id`(`user_id` ASC) USING BTREE,
  INDEX `fk_photos_recipe`(`recipe_id` ASC) USING BTREE,
  CONSTRAINT `fk_photos_recipe` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_photos_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of photos
-- ----------------------------
INSERT INTO `photos` VALUES (1, 1, 'img/demo-dish-1.svg', '番茄牛腩意面：浓郁红酱！', '2026-03-06 16:50:07', NULL);
INSERT INTO `photos` VALUES (2, 2, 'img/demo-dish-2.svg', '蛋炒饭：懒人快手。', '2026-03-06 16:50:07', NULL);
INSERT INTO `photos` VALUES (3, 3, 'img/demo-dish-3.svg', '烤鸡腿：刷汁上色。', '2026-03-06 16:50:07', NULL);
INSERT INTO `photos` VALUES (4, 4, 'img/demo-dish-2.svg', '今天先从水煮蛋开始。', '2026-03-06 17:03:46', NULL);

-- ----------------------------
-- Table structure for recipe_ingredients
-- ----------------------------
DROP TABLE IF EXISTS `recipe_ingredients`;
CREATE TABLE `recipe_ingredients`  (
  `recipe_id` int NOT NULL,
  `ingredient_id` int NOT NULL,
  PRIMARY KEY (`recipe_id`, `ingredient_id`) USING BTREE,
  INDEX `ix_ri_ingredient_id`(`ingredient_id` ASC) USING BTREE,
  CONSTRAINT `fk_ri_ingredient` FOREIGN KEY (`ingredient_id`) REFERENCES `ingredients` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_ri_recipe` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of recipe_ingredients
-- ----------------------------
INSERT INTO `recipe_ingredients` VALUES (3, 1);
INSERT INTO `recipe_ingredients` VALUES (4, 1);
INSERT INTO `recipe_ingredients` VALUES (1, 5);
INSERT INTO `recipe_ingredients` VALUES (1, 6);
INSERT INTO `recipe_ingredients` VALUES (1, 7);
INSERT INTO `recipe_ingredients` VALUES (1, 8);
INSERT INTO `recipe_ingredients` VALUES (2, 8);
INSERT INTO `recipe_ingredients` VALUES (3, 8);
INSERT INTO `recipe_ingredients` VALUES (1, 9);
INSERT INTO `recipe_ingredients` VALUES (2, 9);
INSERT INTO `recipe_ingredients` VALUES (3, 9);
INSERT INTO `recipe_ingredients` VALUES (1, 10);
INSERT INTO `recipe_ingredients` VALUES (2, 10);
INSERT INTO `recipe_ingredients` VALUES (3, 10);
INSERT INTO `recipe_ingredients` VALUES (1, 11);
INSERT INTO `recipe_ingredients` VALUES (1, 12);
INSERT INTO `recipe_ingredients` VALUES (3, 13);
INSERT INTO `recipe_ingredients` VALUES (2, 14);
INSERT INTO `recipe_ingredients` VALUES (2, 15);
INSERT INTO `recipe_ingredients` VALUES (2, 16);
INSERT INTO `recipe_ingredients` VALUES (2, 17);

-- ----------------------------
-- Table structure for recipes
-- ----------------------------
DROP TABLE IF EXISTS `recipes`;
CREATE TABLE `recipes`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(160) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `instructions` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `cooking_time_minutes` int NOT NULL DEFAULT 0,
  `date_created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `author_id` int NULL DEFAULT NULL,
  `country_id` int NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_recipes_title`(`title` ASC) USING BTREE,
  INDEX `fk_recipes_author`(`author_id` ASC) USING BTREE,
  INDEX `fk_recipes_country`(`country_id` ASC) USING BTREE,
  CONSTRAINT `fk_recipes_author` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_recipes_country` FOREIGN KEY (`country_id`) REFERENCES `countries` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of recipes
-- ----------------------------
INSERT INTO `recipes` VALUES (1, '番茄牛腩意面', '1. 牛腩切块焯水；洋葱蒜爆香。\n2. 加入西红柿炒出汁，放入牛腩炖 40 分钟。\n3. 意面煮熟后与酱汁拌匀，黑胡椒调味。', 60, '2026-03-06 16:50:07', 3, 4);
INSERT INTO `recipes` VALUES (2, '蜂蜜柠檬烤鸡腿', '1. 鸡腿划刀，酱油+蜂蜜+柠檬汁+黑胡椒腌 30 分钟。\n2. 200°C 烤 25-30 分钟，中途翻面刷汁。\n3. 出炉静置 5 分钟再切。', 45, '2026-03-06 16:50:07', 1, 2);
INSERT INTO `recipes` VALUES (3, '简单蛋炒饭', '1. 鸡蛋打散炒熟盛出。\n2. 锅里少油，下米饭炒散。\n3. 加入鸡蛋，盐和黑胡椒调味即可。', 15, '2026-03-06 16:50:07', 2, 5);
INSERT INTO `recipes` VALUES (4, '水煮蛋（极简）', '1. 锅中加水烧开。\n2. 放入鸡蛋，小火煮 8-10 分钟。\n3. 捞出过冷水，剥壳即可。', 12, '2026-03-06 17:03:46', 4, 5);

-- ----------------------------
-- Table structure for reviews
-- ----------------------------
DROP TABLE IF EXISTS `reviews`;
CREATE TABLE `reviews`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `recipe_id` int NOT NULL,
  `rating` tinyint NOT NULL DEFAULT 5,
  `comment_text` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_posted` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uq_review_user_recipe`(`user_id` ASC, `recipe_id` ASC) USING BTREE,
  INDEX `ix_reviews_user_id`(`user_id` ASC) USING BTREE,
  INDEX `ix_reviews_recipe_id`(`recipe_id` ASC) USING BTREE,
  CONSTRAINT `fk_reviews_recipe` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_reviews_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of reviews
-- ----------------------------
INSERT INTO `reviews` VALUES (1, 1, 1, 5, '酱汁浓郁，牛腩软烂，配意面太搭了。', '2026-03-06 16:50:07');
INSERT INTO `reviews` VALUES (2, 2, 1, 4, '好吃！我把牛腩换成了牛肉片也不错。', '2026-03-06 16:50:07');
INSERT INTO `reviews` VALUES (3, 3, 2, 5, '酸甜平衡，烤制时间掌握好会非常嫩。', '2026-03-06 16:50:07');
INSERT INTO `reviews` VALUES (4, 1, 4, 5, '极简但很实用，掌握时间就稳了。', '2026-03-06 17:03:46');

-- ----------------------------
-- Table structure for user_recipe_status
-- ----------------------------
DROP TABLE IF EXISTS `user_recipe_status`;
CREATE TABLE `user_recipe_status`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `recipe_id` int NOT NULL,
  `status` enum('wishlist','cooked') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uq_user_recipe_status`(`user_id` ASC, `recipe_id` ASC, `status` ASC) USING BTREE,
  INDEX `ix_user_recipe_status_user_id`(`user_id` ASC) USING BTREE,
  INDEX `ix_user_recipe_status_recipe_id`(`recipe_id` ASC) USING BTREE,
  CONSTRAINT `fk_urs_recipe` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_urs_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of user_recipe_status
-- ----------------------------
INSERT INTO `user_recipe_status` VALUES (1, 1, 1, 'cooked', '2026-03-06 16:50:07');
INSERT INTO `user_recipe_status` VALUES (2, 1, 3, 'wishlist', '2026-03-06 16:50:07');
INSERT INTO `user_recipe_status` VALUES (3, 2, 3, 'cooked', '2026-03-06 16:50:07');
INSERT INTO `user_recipe_status` VALUES (4, 2, 2, 'wishlist', '2026-03-06 16:50:07');
INSERT INTO `user_recipe_status` VALUES (5, 4, 1, 'wishlist', '2026-03-06 17:03:46');
INSERT INTO `user_recipe_status` VALUES (6, 4, 2, 'wishlist', '2026-03-06 17:03:46');
INSERT INTO `user_recipe_status` VALUES (7, 4, 4, 'cooked', '2026-03-06 17:03:46');

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `bio` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `header_photo_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `profile_photo_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `chef_rating` decimal(3, 1) NOT NULL DEFAULT 0.0,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uq_users_username`(`username` ASC) USING BTREE,
  INDEX `ix_users_username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, 'alice', 'pbkdf2:sha256:1000000$DdXVawneXzIDnhkX$bcf5ea409ba6ea80561ebba8c8fff61a9468805f223cc223a9c71a9d8dee14c8', '爱做家常菜，也爱拍照记录。', '', '', 1.0, '2026-03-06 16:50:06');
INSERT INTO `users` VALUES (2, 'bob', 'pbkdf2:sha256:1000000$ZDCswT7EE050YNsS$4da587ae8c2e3f5c6ebb429bee875125e819d2f685eb0298d6265e5bdf2e6e38', '料理新手，擅长清空冰箱。', '', '', 0.8, '2026-03-06 16:50:07');
INSERT INTO `users` VALUES (3, 'chef_lee', 'pbkdf2:sha256:1000000$AySEHulpgleWq1Lg$abe79e21a35dc4fc6a5a19afd39989731cc61904e9258202d0dbcde3ab994fab', '专业厨师：分享高性价比的餐厅级配方。', '', '', 0.6, '2026-03-06 16:50:07');
INSERT INTO `users` VALUES (4, 'admin1', 'pbkdf2:sha256:1000000$rGHSJoTYoDQTx3uo$be604e6d8424cbf72ed8ec616051ef6ef78dd7e01b6a12c4bd3cb8affb6e829c', '管理员/测试账号：用来体验下拉菜单与消息。', '', '', 0.6, '2026-03-06 17:03:46');

SET FOREIGN_KEY_CHECKS = 1;