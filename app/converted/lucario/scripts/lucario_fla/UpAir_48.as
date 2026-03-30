package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class UpAir_48 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;
        public var audio:Number;
        public var playSound:Number;

        public function UpAir_48()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 3, this.frame4, 8, this.frame9, 13, this.frame14, 15, this.frame16, 16, this.frame17, 17, this.frame18, 22, this.frame23, 23, this.frame24);
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
                this.self.updateAuraDamage([1]);
                this.self.updateAuraPaws();
            };
        }

        internal function frame2():*
        {
            this.self.addEffectToList(this.self.attachEffect("trail_lucario_uair", {
                "scaleX":1.15,
                "scaleY":1.15,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame3():*
        {
            this.self.setLandingLag(true);
            this.self.playAttackSound(1);
        }

        internal function frame4():*
        {
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

        internal function frame9():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame14():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame16():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame17():*
        {
            this.self.endAttack();
        }

        internal function frame18():*
        {
            this.self.removeAllEffects();
            this.self.updateAuraPaws();
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_l");
            }
            else
            {
                this.self.playSound("lucario_land02");
            };
        }

        internal function frame23():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }


    }
}

