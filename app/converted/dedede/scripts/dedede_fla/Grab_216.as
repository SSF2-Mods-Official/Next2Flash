package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class Grab_216 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var grabBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var touchBox:MovieClip;
        public var self:DededeExt;
        public var xframe:String;
        public var rand:int;
        public var newStats:Object;

        public function Grab_216()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 3, this.frame4, 4, this.frame5, 15, this.frame16, 16, this.frame17, 21, this.frame22, 22, this.frame23, 36, this.frame37, 37, this.frame38, 38, this.frame39, 39, this.frame40, 40, this.frame41, 44, this.frame45, 55, this.frame56);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.xframe = "grab";
            };
        }

        internal function frame2():*
        {
            if ((this.self.getXSpeed() > 5.5) || (this.self.getXSpeed() < -5.5))
            {
                this.self.setXSpeed((this.self.getXSpeed() * 1.5));
                this.self.stancePlayFrame("dashgrab");
            };
        }

        internal function frame4():*
        {
            this.self.playSound("grab_swing5");
        }

        internal function frame5():*
        {
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-17)});
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }

        internal function frame17():*
        {
            this.xframe = "grab";
        }

        internal function frame22():*
        {
            SSF2API.playSound("grab_swing6");
        }

        internal function frame23():*
        {
            this.self.setXSpeed(0);
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-16),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame37():*
        {
            this.self.endAttack();
        }

        internal function frame38():*
        {
            this.self.addEffectToList(this.self.attachEffect("grabbed_gfx", {
                "x":this.self.flipX(44),
                "y":-25,
                "scaleX":-0.4,
                "scaleY":-0.4
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame39():*
        {
            this.xframe = "grab";
            stop();
            this.rand = 0;
            if (this.self.isCPU() && (this.self.getCPULevel() >= 1))
            {
                this.rand = (10 * SSF2API.random());
                if (this.rand >= 6)
                {
                    this.self.stancePlayFrame("attack");
                };
            };
        }

        internal function frame40():*
        {
            this.self.stancePlayFrame("grabbed2");
        }

        internal function frame41():*
        {
            this.xframe = "attack";
            this.newStats = {"refreshRate":650};
            this.self.updateAttackStats(this.newStats);
            this.self.updateAttackBoxStats(1, {"effect_id":"effect_hit3"});
            this.self.refreshAttackID();
        }

        internal function frame45():*
        {
            SSF2API.getCamera().shake(4);
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-14)});
        }

        internal function frame56():*
        {
            this.self.stancePlayFrame("grabbed2");
        }


    }
}

