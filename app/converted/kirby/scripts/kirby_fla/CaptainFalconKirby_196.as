package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class CaptainFalconKirby_196 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var self:KirbyExt;
        public var groundNormalStats:*;
        public var groundReverseStats:*;
        public var airNormalStats:*;
        public var airReverseStats:*;
        public var reversed:*;
        public var captainfalcon_ground:Boolean;
        public var charge:*;

        public function CaptainFalconKirby_196()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 4, this.frame5, 11, this.frame12, 23, this.frame24, 24, this.frame25, 26, this.frame27, 28, this.frame29, 35, this.frame36, 50, this.frame51, 55, this.frame56, 60, this.frame61);
        }

        public function land(_arg_1:*=null):*
        {
            if (this.reversed)
            {
                this.self.updateAttackBoxStats(1, this.groundReverseStats);
                this.self.updateAttackBoxStats(2, this.groundReverseStats);
            }
            else
            {
                this.self.updateAttackBoxStats(1, this.groundNormalStats);
                this.self.updateAttackBoxStats(2, this.groundNormalStats);
            };
            SSF2API.getCamera().shake(3);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("kirby_land");
            };
        }

        public function unland(_arg_1:*=null):*
        {
            if (this.reversed)
            {
                this.self.updateAttackBoxStats(1, this.airReverseStats);
                this.self.updateAttackBoxStats(2, this.airReverseStats);
            }
            else
            {
                this.self.updateAttackBoxStats(1, this.airNormalStats);
                this.self.updateAttackBoxStats(2, this.airNormalStats);
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.groundNormalStats = {
                "damage":25,
                "direction":40,
                "power":45,
                "kbConstant":100,
                "hitStun":10,
                "selfHitStun":8
            };
            this.groundReverseStats = {
                "damage":28,
                "direction":35,
                "power":50,
                "kbConstant":100,
                "hitStun":11,
                "selfHitStun":9
            };
            this.airNormalStats = {
                "damage":23,
                "direction":40,
                "power":35,
                "kbConstant":100,
                "hitStun":9,
                "selfHitStun":7
            };
            this.airReverseStats = {
                "damage":26,
                "direction":35,
                "power":40,
                "kbConstant":100,
                "hitStun":10,
                "selfHitStun":8
            };
            this.reversed = false;
            if (SSF2API.isReady() && this.self)
            {
                this.captainfalcon_ground = this.self.isOnGround();
                if (!this.captainfalcon_ground)
                {
                    this.self.forceAttack("kirby_captainfalcon_air", null, true);
                };
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.land);
                this.self.addEventListener(SSF2Event.GROUND_LEAVE, this.unland);
            };
        }

        internal function frame2():*
        {
            this.self.playVoiceSound(1);
        }

        internal function frame3():*
        {
            this.charge = this.self.playAttackSound(1);
        }

        internal function frame5():*
        {
            if ((this.self.isFacingRight() && this.self.getControls().LEFT && !this.self.getControls().RIGHT) || (!(this.self.isFacingRight()) && this.self.getControls().RIGHT && !this.self.getControls().LEFT))
            {
                this.self.stancePlayFrame("reversed");
            };
        }

        internal function frame12():*
        {
            if (!this.self.isOnGround())
            {
                this.self.updateAttackStats({"allowControl":true});
            };
        }

        internal function frame24():*
        {
            if (!this.self.isOnGround())
            {
                this.self.updateAttackStats({"allowControl":false});
            };
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame25():*
        {
            this.self.updateAttackStats({"air_ease":0});
            SSF2API.getCamera().shake(6);
            this.self.playVoiceSound(2);
        }

        internal function frame27():*
        {
            this.self.setXSpeed(8, false);
            this.self.playAttackSound(2);
            this.self.playAttackSound(3);
            SSF2API.stopSound(this.charge);
        }

        internal function frame29():*
        {
            this.self.attachEffect("falconAfterEffect");
        }

        internal function frame36():*
        {
            this.self.updateAttackStats({"air_ease":-1});
            if (!this.self.isOnGround())
            {
                this.self.updateAttackStats({"allowControl":true});
            };
        }

        internal function frame51():*
        {
            this.self.endAttack();
        }

        internal function frame56():*
        {
            this.self.flip();
        }

        internal function frame61():*
        {
            this.reversed = true;
            if (this.self.isOnGround())
            {
                this.self.updateAttackBoxStats(1, this.groundReverseStats);
            }
            else
            {
                this.self.updateAttackBoxStats(1, this.airReverseStats);
            };
            this.self.stancePlayFrame("continue");
        }


    }
}

