package kirby_fla
{
    import flash.display.MovieClip;
    import flash.events.Event;

    public dynamic class USpecial_105 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var hand:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var waiting:*;
        public var landingBool:Boolean;
        public var controls:*;

        public function USpecial_105()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 7, this.frame8, 11, this.frame12, 17, this.frame18, 20, this.frame21, 21, this.frame22, 23, this.frame24, 24, this.frame25, 38, this.frame39);
        }

        public function moveDown():void
        {
            this.self.setYSpeed(20);
        }

        public function jumpToContinue(_arg_1:Event=null):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.moveDown);
            this.self.updateAttackStats({"allowControl":false});
            this.self.stancePlayFrame("continue");
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.waiting = false;
            this.landingBool = false;
            if (this.self && SSF2API.isReady())
            {
                this.self.playVoiceSound(1);
                this.self.playAttackSound(1);
                this.controls = this.self.getControls();
                if (this.self.isOnGround() || (this.controls.LEFT == this.controls.RIGHT))
                {
                    this.self.setXSpeed(0);
                };
                this.self.setYSpeed(0);
                this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            };
        }

        internal function frame7():*
        {
            this.self.updateAttackStats({"allowControl":true});
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(2),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame8():*
        {
            this.self.playAttackSound(2);
            this.self.playVoiceSound(2);
            this.self.setYSpeed(-27);
        }

        internal function frame12():*
        {
            this.self.setYSpeed(0);
        }

        internal function frame18():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":2,
                "direction":275,
                "power":0,
                "weightKB":96,
                "kbConstant":100
            });
            this.self.updateAttackBoxStats(2, {
                "damage":2,
                "direction":275,
                "power":0,
                "weightKB":96,
                "kbConstant":100
            });
            this.self.updateAttackBoxStats(3, {
                "damage":2,
                "direction":275,
                "power":0,
                "weightKB":96,
                "kbConstant":100
            });
            this.self.refreshAttackID();
        }

        internal function frame21():*
        {
            this.self.createTimer(1, 0, this.moveDown);
            this.self.playAttackSound(3);
        }

        internal function frame22():*
        {
            this.self.updateAttackStats({"air_ease":-1});
            if (this.self.isOnGround())
            {
                this.jumpToContinue();
            }
            else
            {
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            };
            this.waiting = true;
            stop();
        }

        internal function frame24():*
        {
            this.self.stancePlayFrame("freeze");
        }

        internal function frame25():*
        {
            this.waiting = false;
            play();
            this.self.destroyTimer(this.moveDown);
            this.self.fireProjectile("kirby_swordwave");
            this.self.attachEffect("effect_kirby_land", {"y":-20});
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(2),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
            SSF2API.getCamera().shake(6);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playVoiceSound(3);
                this.self.playAttackSound(4);
            };
        }

        internal function frame39():*
        {
            this.self.endAttack();
        }


    }
}

