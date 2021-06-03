from __future__ import print_function
import sys
import os
import copy
import errno
import PyFBA


def roles_to_model(rolesFile, id, name, orgtype="standard", verbose=False):
    """
    Read in the 'assigned_functions' file from RAST and create a model.

    :param rolesFile: File path to assigned functions RAST file
    :type rolesFile: str
    :param id: Model ID
    :type id: str
    :param name: Model name
    :type name: str
    :param orgtype: Organism type --- standard, kbase, kbase_simple, gram_negative / gramnegative
    :type orgtype: str
    :param verbose: Verbose output
    :type verbose: bool
    :return: The generated model object
    :rtype: Model
    """

    # Load ModelSEED database
    compounds, reactions, enzymes = \
            PyFBA.parse.model_seed.compounds_reactions_enzymes(orgtype)

    # Read in assigned functions file to build set of roles
    assigned_functions = PyFBA.parse.read_assigned_functions(rolesFile)
    roles = set()
    for rs in assigned_functions.values():
        roles.update(rs)

    # Obtain reactions for each role
    # Key is role, value is set of reaction ids
    model_reactions = PyFBA.filters.roles_to_reactions(roles)

    # Create model object
    model = PyFBA.model.Model(id, name, orgtype)
    for role, rxnIDs in model_reactions.items():
        for rxnID in rxnIDs:
            if rxnID in reactions:
                model.add_reactions({reactions[rxnID]})
                model.add_roles({role: {rxnID}})
            elif verbose:
                print("Reaction ID '{}' for role '{}'".format(rxnID, role),
                      "is not in our reactions list. Skipped.",
                      file=sys.stderr)

    # Set biomass equation based on organism type
    biomass_eqn = PyFBA.metabolism.biomass_equation(orgtype)
    model.set_biomass_reaction(biomass_eqn)
    return model

def roles_to_model_new(roles, id, name, orgtype="standard", verbose=False):
    """
    Read in the 'assigned_functions' file from RAST and create a model.

    :param roles: set of functional roles
    :type rolesFile: str
    :param id: Model ID
    :type id: str
    :param name: Model name
    :type name: str
    :param orgtype: Organism type --- standard, kbase, kbase_simple, gram_negative / gramnegative
    :type orgtype: str
    :param verbose: Verbose output
    :type verbose: bool
    :return: The generated model object
    :rtype: Model
    """

    # Load ModelSEED database
    compounds, reactions, enzymes = \
            PyFBA.parse.model_seed.compounds_reactions_enzymes(orgtype)

    # Read in assigned functions file to build set of roles
    # assigned_functions = PyFBA.parse.read_assigned_functions(rolesFile)
    # roles = set()
    # for rs in assigned_functions.values():
    #     roles.update(rs)

    # Obtain reactions for each role
    # Key is role, value is set of reaction ids
    model_reactions = PyFBA.filters.roles_to_reactions(roles)

    # Create model object
    model = PyFBA.model.Model(id, name, orgtype)
    for role, rxnIDs in model_reactions.items():
        for rxnID in rxnIDs:
            if rxnID in reactions:
                model.add_reactions({reactions[rxnID]})
                model.add_roles({role: {rxnID}})
            elif verbose:
                print("Reaction ID '{}' for role '{}'".format(rxnID, role),
                      "is not in our reactions list. Skipped.",
                      file=sys.stderr)

    # Set biomass equation based on organism type
    biomass_eqn = PyFBA.metabolism.biomass_equation(orgtype)
    model.set_biomass_reaction(biomass_eqn)
    return model


def save_model(model, out_dir):
    """
    Save all model information in multiple files.
    This is meant to be temporary until SBML output is functional.

    :param model: Model to save
    :type model: Model
    :param out_dir: Directory to store files
    :type out_dir: str
    """
    import datetime
    dt = datetime.datetime.now()
    prefix = model.name
    # Check if directory exists using method from
    # http://stackoverflow.com/a/5032238
    try:
        os.makedirs(out_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    # Begin by storing basic info
    fname = prefix + ".info"
    with open(os.path.join(out_dir, fname), "w") as f:
        f.write("id\t" + model.id + "\n")
        f.write("name\t" + model.name + "\n")
        f.write("organism_type\t" + model.organism_type + "\n")
        f.write("created_on\t" + dt.isoformat())

    # Store roles -> reaction ID lists
    fname = prefix + ".roles"
    with open(os.path.join(out_dir, fname), "w") as f:
        for rl, rIDs in model.roles.items():
            f.write(rl + "\t" + ";".join(rIDs) + "\n")

    # Store reaction IDs
    fname = prefix + ".reactions"
    with open(os.path.join(out_dir, fname), "w") as f:
        f.write("\n".join(model.reactions.keys()) + "\n")

    # Store compound IDs
    fname = prefix + ".compounds"
    with open(os.path.join(out_dir, fname), "w") as f:
        f.write("\n".join(model.compounds.keys()) + "\n")

    # Store gap-filled media
    fname = prefix + ".gfmedia"
    with open(os.path.join(out_dir, fname), "w") as f:
        if len(model.gapfilled_media) > 0:
            f.write("\n".join(model.gapfilled_media) + "\n")

    # Store gap-filled reaction IDs
    fname = prefix + ".gfreactions"
    with open(os.path.join(out_dir, fname), "w") as f:
        if len(model.gf_reactions) > 0:
            f.write("\n".join(model.gf_reactions) + "\n")


def load_model(in_dir, prefix):
    """
    Load all model information from multiple files generated by
    the "save_model()" function.
    This is meant to be temporary until SBML input is functional.

    :param in_dir: Directory of files
    :type in_dir: str
    :param prefix: Files prefix
    :type prefix: str
    :return: The generated model object
    :rtype: Model
    """

    # Load info
    id = name = orgtype = None
    fname = prefix + ".info"
    with open(os.path.join(in_dir, fname)) as f:
        for l in f:
            item, value = l.rstrip("\n").split("\t", 1)
            if item == "id":
                id = value
            elif item == "name":
                name = value
            elif item == "organism_type":
                orgtype = value
            elif item == "created_on":
                pass  # Only stored for reference purpose

    if not id or not name or not orgtype:
        sys.stderr.write("Could not extract info:\n")
        sys.stderr.write("id:" + id + "\n")
        sys.stderr.write("name:" + name + "\n")
        sys.stderr.write("orgtype:" + orgtype + "\n")
        return None

    # Load roles -> reaction ID lists
    fname = prefix + ".roles"
    mroles = {}
    with open(os.path.join(in_dir, fname)) as f:
        for l in f:
            role, rIDs = l.rstrip("\n").split("\t", 1)
            mroles[role] = rIDs.split(";")

    # Load ModelSEED database
    compounds, reactions, enzymes = \
            PyFBA.parse.model_seed.compounds_reactions_enzymes(orgtype)

    # Load reaction IDs
    fname = prefix + ".reactions"
    mreactions = set()
    with open(os.path.join(in_dir, fname)) as f:
        for l in f:
            rxn = l.rstrip("\n")
            try:
                mreactions.add(reactions[rxn])
            except KeyError:
                sys.stderr.write("Reaction " + rxn + " was not found in the database. Skipping.")

    # Load gap-filled media
    fname = prefix + ".gfmedia"
    gapfilled_media = set()
    with open(os.path.join(in_dir, fname)) as f:
        for l in f:
            gfmed = l.rstrip("\n")
            gapfilled_media.add(gfmed)

    # Load gap-filled reaction IDs
    fname = prefix + ".gfreactions"
    gf_reactions = set()
    with open(os.path.join(in_dir, fname)) as f:
        for l in f:
            gfrxn = l.rstrip("\n")
            gf_reactions.add(gfrxn)

    # Create model object
    model = PyFBA.model.Model(id, name, orgtype)
    model.roles = copy.deepcopy(mroles)
    model.gapfilled_media = copy.copy(gapfilled_media)
    model.gf_reactions = copy.copy(gf_reactions)
    model.add_reactions(mreactions)
    biomass_eqn = PyFBA.metabolism.biomass_equation(orgtype)
    model.set_biomass_reaction(biomass_eqn)

    return model
