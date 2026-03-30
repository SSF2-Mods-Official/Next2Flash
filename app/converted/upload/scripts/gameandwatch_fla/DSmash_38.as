package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class DSmash_38 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;
        public var xframe:String;

        public function DSmash_38()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 44, this.frame45, 45, this.frame46, 48, this.frame49, 58, this.frame59);
        }

        public function effects():void
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-5),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            this.xframe = null;
            if (SSF2API.isReady())
            {
                this.self.attachEffect("global_dust_swirl");
            };
        }

        internal function frame5():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame45():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame46():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
        }

        internal function frame49():*
        {
            this.self.attachEffect("global_dust_cloud");
            this.self.playSound("snd_se_GW_Wave05_Lo");
            this.self.playSound("snd_se_GW_Wave06_Hi");
            this.self.playSound("gw_nairend");
            SSF2API.getCamera().shake(8);
        }

        internal function frame59():*
        {
            this.self.endAttack();
        }


    }
}

