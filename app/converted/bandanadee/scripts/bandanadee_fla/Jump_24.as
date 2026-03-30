package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class Jump_24 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;
        public var xframe:*;
        public var done:*;
        public var fatjump:*;

        public function Jump_24()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 18, this.frame19, 38, this.frame39);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                if (this.self.getGlobalVariable("screwAttackOn"))
                {
                    this.self.endAttack();
                    this.self.forceAttack("item_screw");
                }
                else
                {
                    this.xframe = "midair";
                    this.done = false;
                    this.fatjump = false;
                    this.self.setGlobalVariable("kirbyPeachUsed", false);
                };
            };
        }

        internal function frame2():*
        {
            this.self.playSound("bandanadee_jump1");
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }

        internal function frame39():*
        {
            this.self.endAttack();
        }


    }
}

