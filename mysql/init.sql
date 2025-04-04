-- Tabela principal para armazenar os cálculos de seguro
CREATE TABLE IF NOT EXISTS `insurance_calculations` (
  `id` VARCHAR(36) NOT NULL,                -- UUID 
  `car_make` VARCHAR(50) NOT NULL,
  `car_model` VARCHAR(50) NOT NULL,
  `car_year` INT NOT NULL,
  `car_value` DECIMAL(15, 2) NOT NULL,      
  `applied_rate` DECIMAL(10, 5) NOT NULL,   
  `calculated_premium` DECIMAL(15, 2) NOT NULL, 
  `deductible_value` DECIMAL(15, 2) NOT NULL,  
  `policy_limit` DECIMAL(15, 2) NOT NULL,     
  `broker_fee` DECIMAL(15, 2) NOT NULL,       
  `gis_adjustment` DECIMAL(10, 5) NULL,       
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `deleted_at` TIMESTAMP NULL DEFAULT NULL,      -- Para soft delete
  PRIMARY KEY (`id`),
  INDEX `idx_deleted_at` (`deleted_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela para armazenar os endereços associados aos cálculos (relação 1:1)
CREATE TABLE IF NOT EXISTS `calculation_addresses` (
  `calculation_id` VARCHAR(36) NOT NULL,     
  `street` VARCHAR(255) NOT NULL,
  `number` VARCHAR(20) NOT NULL,
  `complement` VARCHAR(100) NULL,
  `neighborhood` VARCHAR(100) NOT NULL,
  `city` VARCHAR(100) NOT NULL,
  `state` VARCHAR(2) NOT NULL,               -- (ex: SP)
  `postal_code` VARCHAR(10) NOT NULL,
  `country` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`calculation_id`),             
  CONSTRAINT `fk_calculation_address`
    FOREIGN KEY (`calculation_id`)
    REFERENCES `insurance_calculations` (`id`)
    ON DELETE CASCADE                     
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;