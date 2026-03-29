package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class USmash_34 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;
        public var xframe:String;

        public function USmash_34()
        {
            super();
            addFrameScript(0, this.frame1, 9, this.frame10, 49, this.frame50, 50, this.frame51, 52, this.frame53, 61, this.frame62, 70, this.frame71, 110, this.frame111, 111, this.frame112, 112, this.frame113, 121, this.frame122);
        }

        public function effects():void
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(5),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            this.xframe = null;
        }

        internal function frame10():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame50():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame51():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
        }

        internal function frame53():*
        {
            this.self.attachEffect("global_dust_cloud");
            this.self.playSound("gw_usmash");
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            };
        }

        internal function frame62():*
        {
            this.self.endAttack();
        }

        internal function frame71():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame111():*
        {
            this.self.stancePlayFrame("charging_right");
        }

        internal function frame112():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
        }

        internal function frame113():*
        {
            this.self.attachEffect("global_dust_cloud");
            this.self.playSound("gw_usmash");
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            };
        }

        internal function frame122():*
        {
            this.self.endAttack();
        }


    }
}

