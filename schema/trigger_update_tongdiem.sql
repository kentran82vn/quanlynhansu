DELIMITER //

CREATE TRIGGER trg_update_tongdiem
AFTER INSERT ON bangdanhgia
FOR EACH ROW
BEGIN
    -- Cập nhật tổng điểm nếu đã có bản ghi
    UPDATE tongdiem_epa
    SET user_total_score = (
        SELECT SUM(user_score)
        FROM bangdanhgia
        WHERE ten_tk = NEW.ten_tk AND year = NEW.year AND month = NEW.month
    ),
    sup_total_score = (
        SELECT SUM(sup_score)
        FROM bangdanhgia
        WHERE ten_tk = NEW.ten_tk AND year = NEW.year AND month = NEW.month
    )
    WHERE ten_tk = NEW.ten_tk AND year = NEW.year AND month = NEW.month;

    -- Nếu không có bản ghi, thêm mới
    IF ROW_COUNT() = 0 THEN
        INSERT INTO tongdiem_epa (ten_tk, year, month, user_total_score, sup_total_score)
        VALUES (
            NEW.ten_tk,
            NEW.year,
            NEW.month,
            IFNULL(NEW.user_score, 0),
            IFNULL(NEW.sup_score, 0)
        );
    END IF;
END;
//

DELIMITER ;
