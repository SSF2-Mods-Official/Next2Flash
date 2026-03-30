package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class NeutralAir_47 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;
        public var audio:Number;
        public var playSound:Number;

        public function NeutralAir_47()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 5, this.frame6, 6, this.frame7, 13, this.frame14, 15, this.frame16, 20, this.frame21, 21, this.frame22, 25, this.frame26);
        }

        public function soundPlay(_arg_1:int):*
        {
            if (this.audio == _arg_1)
            {
                this.self.setGlobalVariable("audio", 0);
            }
            else
            {
                this.self.playVoiceSound(_arg_1);
                this.self.setGlobalVariable("audio", _arg_1);
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setLandingLag(false);
                this.self.updateAuraDamage([1, 2, 3]);
                this.self.updateAuraPaws();
            };
        }

        internal function frame3():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame4():*
        {
            this.self.playAttackSound(1);
            this.self.updateAuraPaws();
            this.audio = this.self.getGlobalVariable("audio");
            this.playSound = SSF2API.random();
            if (this.playSound <= 0.2)
            {
                this.self.setGlobalVariable("audio", 0);
            }
            else if (this.playSound <= 0.4)
            {
                this.soundPlay(1);
            }
            else if (this.playSound <= 0.6)
            {
                this.soundPlay(2);
            }
            else if (this.playSound <= 0.8)
            {
                this.soundPlay(3);
            }
            else
            {
                this.soundPlay(4);
            };
        }

        internal function frame6():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":(7 * this.self.auraMultiplier),
                "direction":55,
                "kbConstant":60
            });
            this.self.updateAttackBoxStats(2, {
                "damage":(7 * this.self.auraMultiplier),
                "direction":55,
                "kbConstant":60
            });
            this.self.updateAttackBoxStats(3, {
                "damage":(7 * this.self.auraMultiplier),
                "direction":55,
                "kbConstant":60
            });
        }

        internal function frame7():*
        {
            this.self.setLandingLag(true);
        }

        internal function frame14():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame16():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame21():*
        {
            this.self.endAttack();
        }

        internal function frame22():*
        {
            this.self.updateAuraPaws();
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("lucario_land01");
            };
        }

        internal function frame26():*
        {
            this.self.endAttack();
        }


    }
}

