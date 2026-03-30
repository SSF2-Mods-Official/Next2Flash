package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class Jump_36 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;
        public var xframe:*;
        public var done:*;

        public function Jump_36()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 17, this.frame18, 18, this.frame19, 32, this.frame33);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            this.xframe = "midair";
            this.done = false;
            if (parent && SSF2API.isReady() && this.self && this.self.getGlobalVariable("screwAttackOn"))
            {
                this.self.endAttack();
                this.self.forceAttack("item_screw");
            };
        }

        internal function frame4():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_jump01");
            SSF2API.getCamera().shake(2);
        }

        internal function frame18():*
        {
            this.self.endAttack();
        }

        internal function frame19():*
        {
            SSF2API.getCamera().shake(2);
        }

        internal function frame33():*
        {
            this.self.endAttack();
        }


    }
}

