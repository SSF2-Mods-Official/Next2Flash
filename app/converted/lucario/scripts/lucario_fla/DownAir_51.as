package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class DownAir_51 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;
        public var audio:Number;
        public var playSound:Number;

        public function DownAir_51()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 5, this.frame6, 6, this.frame7, 11, this.frame12, 13, this.frame14, 18, this.frame19, 19, this.frame20, 23, this.frame24);
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
            this.self.setLandingLag(true);
            this.self.setYSpeed((this.self.getYSpeed() * 0.25));
            this.self.playAttackSound(1);
            this.self.addEffectToList(this.self.attachEffect("trail_lucario_dair", {
                "scaleX":1.15,
                "scaleY":1.15,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
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
                "damage":(6 * this.self.auraMultiplier),
                "direction":78,
                "power":48,
                "kbConstant":70,
                "hitLag":-1.2,
                "hitStun":3,
                "selfHitStun":1,
                "effectSound":"lucario_hit_ms"
            });
            this.self.updateAttackBoxStats(2, {
                "damage":(6 * this.self.auraMultiplier),
                "direction":275,
                "power":48,
                "kbConstant":70,
                "hitLag":-1,
                "hitStun":7,
                "selfHitStun":4,
                "effectSound":"lucario_hit_ml"
            });
            this.self.refreshAttackID();
        }

        internal function frame7():*
        {
            this.self.setYSpeed((this.self.getYSpeed() * 0.4));
            this.self.playAttackSound(2);
        }

        internal function frame12():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame14():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }

        internal function frame20():*
        {
            this.self.removeAllEffects();
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

        internal function frame24():*
        {
            this.self.endAttack();
        }


    }
}

