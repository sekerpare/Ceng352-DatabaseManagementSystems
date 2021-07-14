
CREATE OR REPLACE FUNCTION update_user() RETURNS TRIGGER AS $update_user$
    BEGIN
        IF (TG_OP = 'INSERT') THEN
            UPDATE Users SET review_count = review_count + 1
                WHERE user_id = NEW.user_id;
        END IF;
        RETURN NEW;
    END;
$update_user$ LANGUAGE plpgsql;
CREATE TRIGGER update_user
AFTER INSERT OR DELETE ON Review
    FOR EACH ROW EXECUTE PROCEDURE update_user();


CREATE FUNCTION noZeroRow() RETURNS trigger AS $noZeroRow$
    BEGIN

        IF NEW.stars = 0 THEN
            DELETE FROM Review
            WHERE user_id=NEW.user_id;
            DELETE FROM Tip
            WHERE user_id=NEW.user_id;
        END IF;
        RETURN NEW;
    END;
$noZeroRow$ LANGUAGE plpgsql;
CREATE TRIGGER noZeroRow
AFTER INSERT OR DELETE ON Review
    FOR EACH ROW EXECUTE PROCEDURE noZeroRow();


CREATE VIEW BusinessCount AS
  SELECT B.business_id,B.business_name,Count(R.review_id)
  FROM Business B, Review R
  WHERE B.business_id=R.business_id
  GROUP BY (B.business_id);
