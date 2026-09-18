-- Script SQL de Criação do Banco de Dados para Sistema de Provas Embaralhadas
-- Compatível com MySQL 8.0+ / MariaDB 10.5+

CREATE DATABASE IF NOT EXISTS `sistema_provas` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `sistema_provas`;

-- 1. Tabela de Usuários (Professores, Coordenadores, Administradores)
CREATE TABLE IF NOT EXISTS `usuarios` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `nome` VARCHAR(120) NOT NULL,
    `email` VARCHAR(150) NOT NULL UNIQUE,
    `senha_hash` VARCHAR(255) NOT NULL,
    `perfil` ENUM('admin', 'coordenador', 'professor') NOT NULL DEFAULT 'professor',
    `criado_em` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Tabela de Disciplinas / Matérias
CREATE TABLE IF NOT EXISTS `disciplinas` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `nome` VARCHAR(100) NOT NULL UNIQUE,
    `codigo` VARCHAR(20) UNIQUE,
    `descricao` VARCHAR(255),
    `criada_em` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.1. Relacionamento de disciplinas atribuídas a cada professor
CREATE TABLE IF NOT EXISTS `usuario_disciplinas` (
    `usuario_id` INT NOT NULL,
    `disciplina_id` INT NOT NULL,
    PRIMARY KEY (`usuario_id`, `disciplina_id`),
    FOREIGN KEY (`usuario_id`) REFERENCES `usuarios`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`disciplina_id`) REFERENCES `disciplinas`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Tabela de Questões
CREATE TABLE IF NOT EXISTS `questoes` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `enunciado` TEXT NOT NULL,
    `disciplina_id` INT NOT NULL,
    `tipo` ENUM('multipla_escolha', 'verdadeiro_falso') NOT NULL DEFAULT 'multipla_escolha',
    `dificuldade` ENUM('facil', 'media', 'dificil') NOT NULL DEFAULT 'media',
    `tags` VARCHAR(255),
    `criado_por` INT NOT NULL,
    `criado_em` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`disciplina_id`) REFERENCES `disciplinas`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`criado_por`) REFERENCES `usuarios`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Tabela de Itens / Alternativas de cada Questão
CREATE TABLE IF NOT EXISTS `itens` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `questao_id` INT NOT NULL,
    `texto` TEXT NOT NULL,
    `correta` BOOLEAN NOT NULL DEFAULT FALSE,
    `ordem_original` INT NOT NULL DEFAULT 1,
    FOREIGN KEY (`questao_id`) REFERENCES `questoes`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Tabela de Provas-Base (O Modelo/Molde)
CREATE TABLE IF NOT EXISTS `provas_base` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `titulo` VARCHAR(150) NOT NULL,
    `disciplina_id` INT NOT NULL,
    `turma` VARCHAR(50) NOT NULL,
    `data_aplicacao` DATE,
    `instrucoes` TEXT,
    `criado_por` INT NOT NULL,
    `criada_em` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`disciplina_id`) REFERENCES `disciplinas`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`criado_por`) REFERENCES `usuarios`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Tabela Pivot: Questões pertencentes à Prova-Base
CREATE TABLE IF NOT EXISTS `provas_base_questoes` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `prova_base_id` INT NOT NULL,
    `questao_id` INT NOT NULL,
    `ordem` INT NOT NULL DEFAULT 1,
    `valor_pontos` DECIMAL(4,2) DEFAULT 1.00,
    FOREIGN KEY (`prova_base_id`) REFERENCES `provas_base`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`questao_id`) REFERENCES `questoes`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6.1. Disciplinas e configuração dos blocos da prova-base
CREATE TABLE IF NOT EXISTS `provas_base_disciplinas` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `prova_base_id` INT NOT NULL,
    `disciplina_id` INT NOT NULL,
    `ordem` INT NOT NULL DEFAULT 1,
    FOREIGN KEY (`prova_base_id`) REFERENCES `provas_base`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`disciplina_id`) REFERENCES `disciplinas`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `provas_base_configuracoes` (
    `prova_base_id` INT PRIMARY KEY,
    `embaralhar_blocos` BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (`prova_base_id`) REFERENCES `provas_base`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Tabela de Provas Geradas (Versões Embaralhadas X)
CREATE TABLE IF NOT EXISTS `provas_geradas` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `prova_base_id` INT NOT NULL,
    `codigo_versao` VARCHAR(50) NOT NULL UNIQUE,
    `numero_versao` INT NOT NULL,
    `seed` VARCHAR(64),
    `criada_em` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`prova_base_id`) REFERENCES `provas_base`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Tabela de Ordem Embaralhada das Questões na Prova Gerada
CREATE TABLE IF NOT EXISTS `provas_geradas_questoes` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `prova_gerada_id` INT NOT NULL,
    `questao_id` INT NOT NULL,
    `ordem_embaralhada` INT NOT NULL,
    FOREIGN KEY (`prova_gerada_id`) REFERENCES `provas_geradas`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`questao_id`) REFERENCES `questoes`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. Tabela de Ordem Embaralhada dos Itens na Prova Gerada
CREATE TABLE IF NOT EXISTS `provas_geradas_itens` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `prova_gerada_id` INT NOT NULL,
    `questao_id` INT NOT NULL,
    `item_id` INT NOT NULL,
    `ordem_embaralhada` INT NOT NULL,
    `letra_atribuida` VARCHAR(5) NOT NULL,
    FOREIGN KEY (`prova_gerada_id`) REFERENCES `provas_geradas`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`questao_id`) REFERENCES `questoes`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`item_id`) REFERENCES `itens`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. Tabela de Gabarito por Versão Gerada
CREATE TABLE IF NOT EXISTS `gabaritos` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `prova_gerada_id` INT NOT NULL,
    `numero_questao` INT NOT NULL,
    `questao_id` INT NOT NULL,
    `item_correto_id` INT NOT NULL,
    `letra_correta` VARCHAR(5) NOT NULL,
    FOREIGN KEY (`prova_gerada_id`) REFERENCES `provas_geradas`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`questao_id`) REFERENCES `questoes`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`item_correto_id`) REFERENCES `itens`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
