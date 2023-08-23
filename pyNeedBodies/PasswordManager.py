import bcrypt

class PasswordManager:
  def __init__(self, _password):
    self.rawPassword = _password
    self.password = _password.encode('UTF-8')
    self.salt = bcrypt.gensalt(rounds=15)
    self.hashed_password = bcrypt.hashpw(self.password, self.salt)

  def Print(self):
    print(f"pswd: {self.rawPassword}")
    print(f"bytes: {self.password}")
    print(f"salt: {self.salt}")
    print(f"hash: {self.hashed_password}")

  def checkPassword(self, attempt, _hash):
    encryptedAttempt = attempt.encode('UTF-8')
    return bcrypt.checkpw(encryptedAttempt, _hash)
  
  def ToJson(self, uid):
    return {
      'id': uid,
      'salt': self.salt,
      'hash': self.hashed_password
    }