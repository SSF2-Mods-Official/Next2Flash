package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class TailsKirby_302 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var self:KirbyExt;
        public var rand:*;
        public var proj:*;
        public var tails_ground:Boolean;
        public var effect:*;
        public var effect2:*;

        public function TailsKirby_302()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 5, this.frame6, 7, this.frame8, 8, this.frame9, 13, this.frame14, 14, this.frame15, 27, this.frame28, 28, this.frame29, 30, this.frame31, 31, this.frame32, 34, this.frame35, 36, this.frame37, 40, this.frame41, 41, this.frame42, 51, this.frame52, 58, this.frame59);
        }

        public function flipX(_arg_1:Number):Number
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.rand = 0;
                this.tails_ground = this.self.isOnGround();
                if (!this.tails_ground)
                {
                    this.self.stancePlayFrame("tails_air");
                };
            };
        }

        internal function frame3():*
        {
            this.self.playSound("tails_blasterpull");
            this.self.attachEffect("global_spark", {
                "x":this.self.flipX(-3),
                "y":-38
            });
        }

        internal function frame6():*
        {
            this.self.playVoiceSound(1);
        }

        internal function frame8():*
        {
            this.self.playSound("tails_blastercharge");
        }

        internal function frame9():*
        {
            this.self.attachEffect("global_sparkle", {
                "x":this.flipX(21),
                "y":-23
            });
        }

        internal function frame14():*
        {
            this.self.fireProjectile("tails_cannon", 5, 0);
            this.self.playAttackSound(1);
        }

        internal function frame15():*
        {
            this.effect = this.self.attachEffect("global_dust_cloud", {
                "x":this.flipX(16),
                "y":-18,
                "scaleX":0.75,
                "scaleY":0.75
            });
            if (this.self.isFacingRight())
            {
                this.effect.rotation = 95;
            }
            else
            {
                this.effect.rotation = (180 - 95);
            };
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame28():*
        {
            this.self.setAttackEnabled(false, "kirby_tails");
            this.self.endAttack();
        }

        internal function frame29():*
        {
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
            };
        }

        internal function frame31():*
        {
            this.self.playSound("tails_blasterpull");
            this.self.attachEffect("global_spark", {
                "x":this.self.flipX(12),
                "y":-42
            });
        }

        internal function frame32():*
        {
            this.self.playVoiceSound(1);
        }

        internal function frame35():*
        {
            this.self.playSound("tails_blastercharge");
        }

        internal function frame37():*
        {
            this.self.attachEffect("global_sparkle", {
                "x":this.flipX(20),
                "y":-11
            });
        }

        internal function frame41():*
        {
            this.self.setAttackEnabled(false, "kirby_tails");
            this.self.updateAttackStats({"allowControl":false});
            this.self.fireProjectile("tails_cannon_air");
            this.self.setXSpeed(-4, false);
            this.self.setYSpeed(-7);
            this.self.playAttackSound(1);
        }

        internal function frame42():*
        {
            this.effect2 = this.self.attachEffect("global_dust_cloud", {
                "x":this.flipX(16),
                "y":-18,
                "scaleX":0.75,
                "scaleY":0.75
            });
            if (this.self.isFacingRight())
            {
                this.effect2.rotation = 345;
            }
            else
            {
                this.effect2.rotation = (180 - 345);
            };
        }

        internal function frame52():*
        {
            this.self.updateAttackStats({"allowControl":true});
        }

        internal function frame59():*
        {
            this.self.endAttack();
        }


    }
}

