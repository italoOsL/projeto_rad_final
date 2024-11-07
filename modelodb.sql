
CREATE TABLE IF NOT EXISTS usuario (
    id INT PRIMARY KEY AUTO_INCREMENT,
    matricula INT UNIQUE,
    nome VARCHAR(100) NOT NULL,
    senha VARCHAR(100) NOT NULL,
    tipo ENUM('aluno', 'professor') NOT NULL
);


CREATE TABLE IF NOT EXISTS nota (
    id INT PRIMARY KEY AUTO_INCREMENT,
    matricula INT NOT NULL,
    avaliacao1 FLOAT DEFAULT NULL,
    avaliacao2 FLOAT DEFAULT NULL,
    FOREIGN KEY (matricula) REFERENCES usuario(matricula)
);