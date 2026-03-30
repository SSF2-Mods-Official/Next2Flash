package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class PeachKirby_280 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var counterBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var power:*;
        public var kbConstant:*;
        public var damage:*;
        public var used:Boolean;
        public var peach_used:Boolean;
        public var peach_grounded:Boolean;

        public function PeachKirby_280()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 5, this.frame6, 28, this.frame29, 29, this.frame30, 30, this.frame31, 34, this.frame35, 42, this.frame43, 53, this.frame54);
        }

        public function flipX(_arg_1:Number):*
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        public function counter(_arg_1:*):*
        {
            this.self.setIntangibility(true);
            this.self.removeEventListener(SSF2Event.CHAR_COUNTER, this.counter);
            this.power = _arg_1.data.attackBoxData.power;
            if (this.power < 10)
            {
                this.power = 10;
            };
            if (this.power > 50)
            {
                this.power = 50;
            };
            this.kbConstant = (_arg_1.data.attackBoxData.kbConstant * 1.2);
            if (this.kbConstant < 60)
            {
                this.kbConstant = 60;
            };
            if (this.kbConstant > 80)
            {
                this.kbConstant = 80;
            };
            this.damage = (_arg_1.data.attackBoxData.damage / 2);
            if (this.damage < 2)
            {
                this.damage = 2;
            };
            if (this.damage > 4)
            {
                this.damage = 4;
            };
            if (_arg_1.data.receiver.getX() < this.self.getX())
            {
                this.self.faceLeft();
            }
            else
            {
                this.self.faceRight();
            };
            SSF2API.print(((((("COUNTER!!! " + this.damage) + "/") + this.kbConstant) + "/") + this.power));
            _arg_1.data.receiver.forceHitStun(10, 0);
            this.self.forceHitStun(5, 0);
            this.self.updateAttackBoxStats(1, {
                "damage":this.damage,
                "kbConstant":this.kbConstant,
                "power":this.power
            });
            this.self.stancePlayFrame("counter");
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.power = 50;
            this.kbConstant = 30;
            this.damage = 4;
            if (SSF2API.isReady() && this.self)
            {
                this.used = this.self.getGlobalVariable("used");
                this.peach_used = this.self.getGlobalVariable("kirbyPeachUsed");
                this.self.addEventListener(SSF2Event.CHAR_COUNTER, this.counter, null);
            };
        }

        internal function frame3():*
        {
            this.self.attachEffect("global_spark", {
                "x":this.flipX(25),
                "y":-25
            });
        }

        internal function frame6():*
        {
            this.peach_grounded = this.self.isOnGround();
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_cloud");
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(25),
                "y":-20,
                "parentLock":true
            });
            this.self.setGlobalVariable("kirbyPeachUsed", true);
            if (!(this.peach_used) && !(this.peach_grounded))
            {
                this.self.setYSpeed(-6);
            };
        }

        internal function frame29():*
        {
            this.self.endAttack();
        }

        internal function frame30():*
        {
            this.self.playAttackSound(2);
            SSF2API.getCamera().shake(5);
        }

        internal function frame31():*
        {
            this.self.attachEffect("global_dust_cloud");
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame35():*
        {
            this.self.setInvincibility(false);
        }

        internal function frame43():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":(this.damage / 2),
                "power":50,
                "direction":30,
                "hitStun":3,
                "selfHitStun":3
            });
            this.self.refreshAttackID();
        }

        internal function frame54():*
        {
            this.self.endAttack();
        }


    }
}

