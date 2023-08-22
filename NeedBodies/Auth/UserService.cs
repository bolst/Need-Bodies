namespace NeedBodies.Auth
{
    public class UserService
    {
        private List<User> _users;

        public UserService(List<User> users)
        {
            _users = users;
        }

        public User? GetByName(string name)
        {
            return _users.FirstOrDefault(x => x.Name == name);
        }

        public User? GetByID(string ID)
        {
            return _users.FirstOrDefault(x => x.ID == ID);
        }

        public User? GetByEmail(string email)
        {
            return _users.FirstOrDefault(x => x.Email == email);
        }

        public void addUser(User newUser)
        {
            _users.Add(newUser);
        }
    }


}