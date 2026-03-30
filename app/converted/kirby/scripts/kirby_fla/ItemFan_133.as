package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemFan_133 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;

        public function ItemFan_133()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 5, this.frame6);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
        }

        internal function frame3():*
        {
            this.self.getItem().activateItem();
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-12)});
        }

        internal function frame4():*
        {
            this.self.getItem().deactivateItem();
        }

        internal function frame6():*
        {
            this.self.endAttack();
        }


    }
}

