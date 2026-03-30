package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class NSpecial_104 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var grabBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var kirbyForce:String;
        public var inhaledOpponent:*;
        public var xframe:*;
        public var action:String;
        public var waiting:Boolean;
        public var hasHit:Boolean;
        public var inhaling:*;
        public var power:String;
        public var continuePlaying:Boolean;
        public var handled:Boolean;
        public var controls:Object;
        public var sfxStop:Number;
        public var sfxStop2:Number;
        public var stats1:Object;
        public var stats2:Object;

        public function NSpecial_104()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 6, this.frame7, 10, this.frame11, 14, this.frame15, 15, this.frame16, 18, this.frame19, 22, this.frame23, 26, this.frame27, 37, this.frame38, 38, this.frame39, 45, this.frame46, 46, this.frame47, 47, this.frame48, 57, this.frame58, 58, this.frame59, 62, this.frame63, 67, this.frame68, 68, this.frame69);
        }

        public function stopSfx(_arg_1:*=null):*
        {
            if ((this.self.getCurrentAnimation() != "b") && (this.self.getCurrentAnimation() != "b_air"))
            {
                SSF2API.stopSound(this.sfxStop);
                this.self.destroyTimer(this.stopSfx);
            };
        }

        public function grabFoe(_arg_1:*=null):*
        {
            if (this.self.getGrabbedOpponents()[0])
            {
                this.self.playAttackSound(3);
            };
            if ((this.self.getCurrentAnimation() != "b") && (this.self.getCurrentAnimation() != "b_air"))
            {
                this.self.destroyTimer(this.grabFoe);
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (parent && SSF2API.isReady() && this.self && (this.self.getCurrentKirbyPower() != null))
            {
                this.kirbyForce = ("kirby_" + this.self.getCurrentKirbyPower());
                this.self.forceAttack(this.kirbyForce, null, true);
                gotoAndStop("failed");
            };
            this.xframe = "sucking";
            this.action = null;
            this.waiting = false;
            this.hasHit = false;
            this.inhaling = false;
            this.power = null;
            this.continuePlaying = false;
            this.handled = true;
            this.controls = null;
            this.stats1 = null;
            this.stats2 = null;
        }

        internal function frame5():*
        {
            this.sfxStop = this.self.playAttackSound(1);
            this.self.setGlobalVariable("SlowCharge", null);
            this.self.createTimer(1, -1, this.stopSfx, {"persistent":true});
            this.self.createTimer(1, -1, this.grabFoe, {"persistent":true});
        }

        internal function frame7():*
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(2),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame11():*
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(2),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame15():*
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(2),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame16():*
        {
            this.inhaling = true;
        }

        internal function frame19():*
        {
            this.sfxStop2 = this.self.playAttackSound(2);
            SSF2API.stopSound(this.sfxStop);
            this.handled = false;
            this.continuePlaying = false;
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(2),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame23():*
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(2),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame27():*
        {
            SSF2API.stopSound(this.sfxStop2);
            if (this.continuePlaying)
            {
                gotoAndStop("suckagain");
            };
        }

        internal function frame38():*
        {
            this.self.endAttack();
        }

        internal function frame39():*
        {
            this.xframe = "swallow";
            this.self.updateAttackBoxStats(1, {
                "hasEffect":true,
                "direction":60,
                "power":75,
                "bypassNonGrabbed":true
            });
            SSF2API.stopSound(this.sfxStop);
            SSF2API.stopSound(this.sfxStop2);
        }

        internal function frame46():*
        {
            this.self.refreshAttackID();
        }

        internal function frame47():*
        {
            this.inhaledOpponent = this.self.getGrabbedOpponent();
            if (this.inhaledOpponent)
            {
                this.inhaledOpponent.setX(this.self.getX());
                this.inhaledOpponent.setY(this.self.getY());
            };
        }

        internal function frame48():*
        {
            this.self.updateAttackStats({"invincible":true});
            this.self.KirbyPower = this.power;
            if (this.power == null)
            {
                this.self.playAttackSound(6);
            }
            else
            {
                this.self.playAttackSound(5);
            };
            this.self.releaseOpponent();
            SSF2API.getCamera().shake(5);
        }

        internal function frame58():*
        {
            this.self.updateAttackStats({"invincible":false});
            this.self.endAttack();
        }

        internal function frame59():*
        {
            this.xframe = "spit";
        }

        internal function frame63():*
        {
            this.self.playAttackSound(4);
            this.inhaledOpponent = this.self.getGrabbedOpponent();
            if (this.inhaledOpponent)
            {
                this.inhaledOpponent.setX(this.self.getX());
                this.inhaledOpponent.setY(this.self.getY());
            };
            this.self.shootOutOpponent();
        }

        internal function frame68():*
        {
            this.self.endAttack();
        }

        internal function frame69():*
        {
            this.self.endAttack();
        }


    }
}

