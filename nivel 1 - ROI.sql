--Nível 1
--ROI
-- ROI médio, maior ROI, menor ROI
SELECT
    ROUND(AVG(roi), 2) AS roi_medio,
    MAX(roi) AS maior_roi,
    MIN(roi) AS menor_roi
FROM fact_campaign;