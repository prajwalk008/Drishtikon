const getContacts = (req, res) => {
    res.json({ message: "Fetching all contacts" });
};

const addContact = (req, res) => {
    const { name, phone } = req.body;
    res.json({ message: `Contact added: ${name}, ${phone}` });
};

module.exports = { getContacts, addContact };
