package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_utilt_35 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_utilt_35()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 4, this.frame5, 5, this.frame6, 12, this.frame13, 13, this.frame14);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
        }

        internal function frame4():*
        {
            this.self.attachEffect("global_dust_cloud", {
                "scaleX":0.5,
                "scaleY":0.5
            });
        }

        internal function frame5():*
        {
            this.self.addEffectToList(this.self.attachEffect("trail_bbm_utilt", {
                "scaleX":1.35,
                "scaleY":1.35,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame6():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame13():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m1");
            }
            else
            {
                this.self.playSound("bomberman_landHeavy");
            };
        }

        internal function frame14():*
        {
            this.self.endAttack();
        }


    }
}

