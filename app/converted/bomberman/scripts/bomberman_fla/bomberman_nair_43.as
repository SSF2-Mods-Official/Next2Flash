package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_nair_43 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_nair_43()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 4, this.frame5, 11, this.frame12, 13, this.frame14, 14, this.frame15, 19, this.frame20);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setLandingLag(false);
            };
        }

        internal function frame3():*
        {
            this.self.setLandingLag(true);
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(30),
                "y":-10,
                "parentLock":true
            });
            this.self.addEffectToList(this.self.attachEffect("trail_bbm_nair", {
                "scaleX":1.35,
                "scaleY":1.35,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame5():*
        {
            this.self.updateAttackBoxStats(1, {
                "direction":80,
                "damage":7,
                "effect_id":"effect_hit2",
                "effectSound":"brawl_kick_s"
            });
            this.self.updateAttackBoxStats(2, {
                "direction":80,
                "damage":7,
                "effect_id":"effect_hit2",
                "effectSound":"brawl_kick_s"
            });
        }

        internal function frame12():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame14():*
        {
            this.self.endAttack();
        }

        internal function frame15():*
        {
            this.self.removeAllEffects();
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("bomberman_landHeavy");
            };
        }

        internal function frame20():*
        {
            this.self.endAttack();
        }


    }
}

