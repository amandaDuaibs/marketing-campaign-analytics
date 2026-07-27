--Nível 1 
-- Empresas
-- Quantas empresas participaram?
SELECT count(*) as Total_empresas from dim_company;
-- Campanhas por empresa
SELECT
    co.company_name,
    COUNT(*) AS total_campanhas
FROM fact_campaign fc
JOIN dim_company co ON fc.id_company = co.id_company
GROUP BY co.company_name
ORDER BY total_campanhas DESC;