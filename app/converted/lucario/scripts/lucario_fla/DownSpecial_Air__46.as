package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class DownSpecial_Air__46 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;
        public var hit:Boolean;
        public var back:Boolean;
        public var controls:*;
        public var audio:int;
        public var playSound:Number;

        public function DownSpecial_Air__46()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 3, this.frame4, 4, this.frame5, 10, this.frame11, 11, this.frame12, 12, this.frame13, 13, this.frame14, 17, this.frame18, 20, this.frame21, 25, this.frame26, 28, this.frame29, 31, this.frame32);
        }

        public function toGround(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
            this.self.removeEventListener(SSF2Event.ATTACK_HIT, this.onHit);
            if (this.hit)
            {
                this.self.toLand();
            }
            else
            {
                this.self.setGlobalVariable("LucarioDSpecFrame", currentFrame);
                this.self.setGlobalVariable("LucarioDSpecBack", this.back);
                this.self.setGlobalVariable("LucarioDSpecAtkID", this.self.getAttackStat("atk_id"));
                this.self.forceAttack("b_down", null, true);
            };
        }

        public function onHit(_arg_1:*=null):*
        {
            this.self.setXSpeed((this.self.getXSpeed() * 0.4));
            this.hit = true;
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
            this.hit = false;
            this.back = false;
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraDamage([1]);
                this.self.updateAttackBoxStats(1, {"paralysis":(14 + (18 * this.self.auraPercentage))});
                this.self.updateAuraPaws();
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
                this.self.addEventListener(SSF2Event.ATTACK_HIT, this.onHit);
            };
        }

        internal function frame2():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame3():*
        {
            this.self.setInvincibility(true);
        }

        internal function frame4():*
        {
            this.controls = this.self.getControls();
            if (this.controls.RIGHT != this.controls.LEFT)
            {
                if (this.controls.RIGHT == this.self.isFacingRight())
                {
                    this.self.setXSpeed(8, false);
                }
                else
                {
                    this.back = true;
                    this.self.setXSpeed(-8, false);
                };
            };
        }

        internal function frame5():*
        {
            this.self.setIntangibility(true);
            this.self.setInvincibility(false);
        }

        internal function frame11():*
        {
            this.self.addEffectToList(this.self.attachEffect("trail_lucario_dspecair", {
                "scaleX":1.15,
                "scaleY":1.15,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame12():*
        {
            this.controls = this.self.getControls();
            if (this.back && (this.controls.RIGHT != this.controls.LEFT) && (this.controls.RIGHT == this.self.isFacingRight()))
            {
                this.self.setXSpeed(9.6, false);
            };
        }

        internal function frame13():*
        {
            this.self.setYSpeed(0);
            this.self.playAttackSound(2);
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

        internal function frame14():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame18():*
        {
            if (this.hit)
            {
                this.self.stancePlayFrame("skip1");
            };
        }

        internal function frame21():*
        {
            this.self.updateAttackStats({"air_ease":-1});
        }

        internal function frame26():*
        {
            if (this.hit)
            {
                this.self.stancePlayFrame("skip2");
            };
        }

        internal function frame29():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame32():*
        {
            this.self.endAttack();
        }


    }
}

