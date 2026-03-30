package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class Ganondorf_Kirby_324 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var groundNormalStats:*;
        public var groundReverseStats:*;
        public var airNormalStats:*;
        public var airReverseStats:*;
        public var reversed:*;

        public function Ganondorf_Kirby_324()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 13, this.frame14, 15, this.frame16, 17, this.frame18, 18, this.frame19, 19, this.frame20, 20, this.frame21, 21, this.frame22, 22, this.frame23, 23, this.frame24, 24, this.frame25, 25, this.frame26, 26, this.frame27, 27, this.frame28, 31, this.frame32, 32, this.frame33, 33, this.frame34, 34, this.frame35, 37, this.frame38, 38, this.frame39, 50, this.frame51, 55, this.frame56, 60, this.frame61);
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
                "damage":32,
                "direction":50,
                "power":120,
                "kbConstant":46
            };
            this.groundReverseStats = {
                "damage":37,
                "direction":40,
                "power":30,
                "kbConstant":100
            };
            this.airNormalStats = {
                "damage":38,
                "direction":30,
                "power":30,
                "kbConstnat":100
            };
            this.airReverseStats = {
                "damage":40,
                "direction":30,
                "power":40,
                "kbConstant":100
            };
            this.reversed = false;
            if (SSF2API.isReady() && this.self)
            {
                this.self.playSound("ganondorf_nspec1");
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.land);
                this.self.addEventListener(SSF2Event.GROUND_LEAVE, this.unland);
                if (!this.self.getMetalStatus())
                {
                    this.self.playSound("kirby_ganondorf_nspec1", true);
                };
            };
        }

        internal function frame6():*
        {
            if ((this.self.isFacingRight() && this.self.getControls().LEFT && !this.self.getControls().RIGHT) || (!(this.self.isFacingRight()) && this.self.getControls().RIGHT && !this.self.getControls().LEFT))
            {
                this.self.stancePlayFrame("reversed");
            }
            else
            {
                this.self.updateAttackStats({"superArmor":true});
            };
        }

        internal function frame14():*
        {
            SSF2API.getCamera().shake(1);
        }

        internal function frame16():*
        {
            SSF2API.getCamera().shake(1);
        }

        internal function frame18():*
        {
            SSF2API.getCamera().shake(1);
        }

        internal function frame19():*
        {
            SSF2API.getCamera().shake(1);
        }

        internal function frame20():*
        {
            SSF2API.getCamera().shake(1);
        }

        internal function frame21():*
        {
            SSF2API.getCamera().shake(1);
        }

        internal function frame22():*
        {
            SSF2API.getCamera().shake(3);
        }

        internal function frame23():*
        {
            SSF2API.getCamera().shake(2);
        }

        internal function frame24():*
        {
            SSF2API.getCamera().shake(1);
        }

        internal function frame25():*
        {
            SSF2API.getCamera().shake(1);
        }

        internal function frame26():*
        {
            SSF2API.getCamera().shake(1);
        }

        internal function frame27():*
        {
            SSF2API.getCamera().shake(1);
        }

        internal function frame28():*
        {
            SSF2API.getCamera().shake(1);
        }

        internal function frame32():*
        {
            this.self.updateAttackStats({"superArmor":false});
        }

        internal function frame33():*
        {
            this.self.setXSpeed(18, false);
            this.self.playSound("ganondorf_nspec2");
            this.self.updateAttackStats({"air_ease":0});
            SSF2API.getCamera().shake(10);
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("kirby_ganondorf_nspec2", true);
            };
        }

        internal function frame34():*
        {
            this.self.setXSpeed(0);
        }

        internal function frame35():*
        {
            SSF2API.getCamera().shake(8);
        }

        internal function frame38():*
        {
            SSF2API.getCamera().shake(5);
        }

        internal function frame39():*
        {
            this.self.updateAttackStats({"air_ease":-1});
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
            this.self.updateAttackStats({"superArmor":true});
            this.self.stancePlayFrame("continue");
        }


    }
}

