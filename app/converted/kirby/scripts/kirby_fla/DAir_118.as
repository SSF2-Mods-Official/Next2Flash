package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class DAir_118 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;

        public function DAir_118()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 5, this.frame6, 6, this.frame7, 8, this.frame9, 11, this.frame12, 14, this.frame15, 17, this.frame18, 20, this.frame21, 23, this.frame24, 28, this.frame29, 29, this.frame30, 37, this.frame38);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.attachEffect("dairSparkle", {"resize":false});
            };
            if (this.self && SSF2API.isReady())
            {
                this.self.setLandingLag(false);
            };
        }

        internal function frame2():*
        {
            this.self.playVoiceSound(1);
        }

        internal function frame6():*
        {
            this.self.setLandingLag(true);
        }

        internal function frame7():*
        {
            this.self.playAttackSound(1);
            this.self.addEffectToList(this.self.attachEffect("global_dust_spiral", {
                "x":this.self.flipX(3),
                "rotation":this.self.flipX(-15),
                "scaleX":1.2,
                "scaleY":1.35,
                "parentLock":true,
                "syncHitStun":true,
                "loop":2
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame9():*
        {
            this.self.refreshAttackID();
        }

        internal function frame12():*
        {
            this.self.refreshAttackID();
        }

        internal function frame15():*
        {
            this.self.refreshAttackID();
        }

        internal function frame18():*
        {
            this.self.refreshAttackID();
        }

        internal function frame21():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":2,
                "direction":270,
                "kbConstant":110
            });
            this.self.updateAttackBoxStats(2, {
                "damage":2,
                "direction":270,
                "kbConstant":110
            });
            this.self.refreshAttackID();
        }

        internal function frame24():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame29():*
        {
            this.self.endAttack();
        }

        internal function frame30():*
        {
            this.self.removeAllEffects();
            this.self.attachEffect("effect_kirby_land", {"y":-20});
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("kirby_land1");
            };
            this.self.updateAttackBoxStats(1, {
                "damage":2,
                "weightKB":40,
                "kbConstant":100,
                "power":0,
                "direction":60,
                "hitStun":-1,
                "selfHitStun":-1,
                "hitLag":-1
            });
            this.self.refreshAttackID();
        }

        internal function frame38():*
        {
            this.self.endAttack();
        }


    }
}

