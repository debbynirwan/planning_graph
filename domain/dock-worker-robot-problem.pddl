;; a simple DWR problem with 2 robots and 2 locations
(define (problem dwrpb1)
  (:domain dock-worker-robot-simple)

  (:objects
   robr robq - robot
   loc1 loc2 - location
   conta contb - container)

  (:init
   (adjacent loc1 loc2)
   (adjacent loc2 loc1)

   (in conta loc1)
   (in contb loc2)

   (atl robr loc1)
   (atl robq loc2)

   (unloaded robr)
   (unloaded robq)
   )

;; a2, b1
  (:goal
    (and
      (in contb loc1)
	  (in conta loc2)
	    )) )
