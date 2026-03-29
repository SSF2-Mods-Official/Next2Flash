package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class Jump_41 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;
        public var xframe:*;
        public var done:*;

        public function Jump_41()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 18, this.frame19, 37, this.frame38);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
            this.xframe = "midair";
            this.done = false;
            if (SSF2API.isReady() && this.self && this.self.getGlobalVariable("screwAttackOn"))
            {
                this.self.endAttack();
                this.self.forceAttack("item_screw");
            };
        }

        internal function frame3():*
        {
            this.self.playSound("falcon_jumpS1");
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }

        internal function frame38():*
        {
            this.self.endAttack();
        }


    }
}

