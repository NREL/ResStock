Increasing Upgrade Options
==========================

To allow more options per upgrade, increase the value returned by the following method defined in ``measures/ApplyUpgrade/resources/constants.rb``:

.. code::

  def self.NumApplyUpgradeOptions
    return 25
  end
  
Then run ``openstudio tasks.rb update_measures``. See :doc:`running_tasks` for instructions on how to run tasks.
