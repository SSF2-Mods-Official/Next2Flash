package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_ftilt_28 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_ftilt_28()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 4, this.frame5, 5, this.frame6, 15, this.frame16, 16, this.frame17);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
        }

        internal function frame3():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame5():*
        {
            this.self.attachEffect("global_dust_light");
            this.self.addEffectToList(this.self.attachEffect("trail_bbm_ftilt", {
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

        internal function frame16():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            };
        }

        internal function frame17():*
        {
            this.self.endAttack();
        }


    }
}

