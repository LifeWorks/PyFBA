
COMMON_REACTION_LIMIT = 5


class Compound:
    """
    A compound is the essential metabolic compound that is involved in a reaction.

    The compound by itself does not have a location. See PyFBA.metabolism.CompoundWithLocation for that detail.
    This abstraction allows us to create Compound objects and then create separate objects with a location
    that are required for the FBA

    Other variables associated with the Compound class:
    :ivar name: the name of the  compound
    :ivar reactions: a set of reaction objects that this compound is connected to
    :ivar model_seed_id: the compound id from the model seed.
    :ivar abbreviation: a short name for the compound
    :ivar formula: the compounds formula
    :ivar mw: the molecular weight of the compound
    :ivar common: Boolean: this is a common compound. This means the coompound is in > COMMON_REACTION_LIMIT reactions
    :ivar charge: the charge associated with the compound

    """

    def __init__(self, cpd_id, name):
        """
        Initiate the object
        :param cpd_id: The id of the compound
        :type cpd_id: str
        :param name: The name of the compound
        :type name: str
        :return:
        :rtype:
        """
        self.id = cpd_id
        self.name = name
        self.reactions = set()
        self.model_seed_id = self.id
        self.alternate_seed_ids = set()
        self.abbreviation = None
        self.formula = None
        self.mw = 0
        self.common = False
        self.charge = 0
        self.is_cofactor = False
        self.linked_compound = False
        self.pka = 0
        self.pkb = 0
        self.is_obsolete = False
        self.abstract_compound = False
        self.is_core = False
        self.inchikey = 0

    def __eq__(self, other):
        """
        Two compounds are equal if they have the same id or the same name

        :param other: The other compound
        :type other: Compound
        :return: If they are equal
        :rtype: bool
        """
        if isinstance(other, Compound):
            return self.id == other.id or self.name == other.name
        else:
            raise NotImplementedError(f"Comparing a Compound with {type(other)} has not been implemented")
    
    def __cmp__(self, other):
        """
        Compare whether two things are the same.

        :param other: The other compound
        :type other: Compound
        :return: An int, zero if they are the same
        :rtype: int
        """
        if isinstance(other, Compound):
            if __eq__(other):
                return 0
            else:
                return 1
        else:
            raise NotImplementedError(f"Comparing a Compound with {type(other)} has not been implemented")

    def __ne__(self, other):
        """
        Are these not equal?

        :param other: The other compound
        :type other: Compound
        :return: If they are not equal
        :rtype: bool
        """
        try:
            result = self.__eq__(other)
        except NotImplementedError:
            return True
        return not result

    def __hash__(self):
        """
        The hash function is based on the name of the compound.

        :rtype: int
        """
        return hash((self.id, self.name))

    def __str__(self):
        """
        The to string function.
        :rtype: str
        """
        return f"{self.id}: {self.name}"

    def __iter__(self):
        for i in self.__dict__.items():
            yield i

    def add_reactions(self, rxns):
        """
        Add a reaction that this compound is involved in. You  can add a set of reactions. See the note above about the
        number of reactions.

        :param rxns: A set of reactions
        :type rxns: set
        """
        if isinstance(rxns, set):
            self.reactions.update(rxns)
        else:
            raise TypeError("You need to add a set of reactions to a compound")

    def has_reaction(self, rxn):
        """
        Is this compound involved in this reaction?

        :param rxn: A Reaction object
        :type rxn: Reaction
        :return: Whether the reaction is present
        :rtype: bool
        """
        return rxn in self.reactions

    def number_of_reactions(self):
        """
        How many reactions is this compound involved in?

        :rtype: int
        """
        return len(self.reactions)

    def all_reactions(self):
        """
        Return a set of all the reactions that this compound is involved in

        :rtype: int
        """
        return self.reactions

    def is_common(self, rct_limit=COMMON_REACTION_LIMIT):
        """
        Is this a common compound? This requires that you have
        added reactions to this compound.
        
        You can either specify the number of reactions or use our
        default that is currently 50.

        :param rct_limit: The limit for a compound to be considered common
        :type rct_limit: int
        :return: Whether this is a common reaction
        :rtype: bool
        """
        if self.number_of_reactions() > rct_limit:
            self.common = True
        else:
            self.common = False
        return self.common

    def calculate_molecular_weight(self):
        """
        Calculate and return the molecular weight of this compound

        :return: The molecular weight
        :rtype: float
        """

        raise NotImplementedError("Sorry. Calculate molecular weight has not yet been implemented.")

    def add_attribute(self, key, value):
        """
        Add an attribute to this class
        """
        setattr(self, key, value)

    def get_attribute(self, key):
        """
        Retrieve an attribute
        """
        return getattr(self, key)


class CompoundWithLocation(Compound):
    """
    Compounds can have several locations:

    A compound has at the very minimum a name and a location. The location is typically one of:
       * e: extracellular
       * c: cytoplasmic
       * h: chloroplast
       * p: periplasm

    We extend the Compound class to add a location, and override a few of the methods

    :ivar location: the location of the compound.
    """

    def calculate_molecular_weight(self):
        pass

    def __init__(self, compound, location):
        """
        Initiate the object

        :param compound: the parent compound. Note you should create this first if it doesn't exist!
        :type cpd_id: PyFBA.metabolism.Compound
        :param location: The location of the compound
        :type location: str
        :return:
        :rtype:
        """
        super().__init__(compound.id, compound.name)
        for it in super():
            self.add_attribute(*it)
        self.location = location

    def __eq__(self, other):
        """
        Two compounds are equal if they have the same name and the same location

        :param other: The other compound
        :type other: Compound
        :return: If they are equal
        :rtype: bool
        """
        if isinstance(other, CompoundWithLocation):
            return self.id == other.id or (self.name, self.location) == (other.name, other.location)
        else:
            raise NotImplementedError(f"Comparing a Compound with {type(other)} has not been implemented")

    def __cmp__(self, other):
        """
        Compare whether two things are the same.

        :param other: The other compound
        :type other: Compound
        :return: An int, zero if they are the same
        :rtype: int
        """
        if isinstance(other, CompoundWithLocation):
            if __eq__(other):
                return 0
            else:
                return 1
        else:
            raise NotImplementedError(f"Comparing a Compound with {type(other)} has not been implemented")

    def __ne__(self, other):
        """
        Are these not equal?

        :param other: The other compound
        :type other: Compound
        :return: If they are not equal
        :rtype: bool
        """
        try:
            result = self.__eq__(other)
        except NotImplementedError:
            return True
        return not result

    def __hash__(self):
        """
        The hash function is based on the name of the compound.

        :rtype: int
        """
        return hash((self.id, self.name, self.location))

    def __str__(self):
        """
        The to string function.
        :rtype: str
        """
        return f"{self.id}: {self.name} (location: {self.location})"
