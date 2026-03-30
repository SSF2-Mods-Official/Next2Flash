package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class NSpecBomb_119 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var self:*;
        public var scale:*;
        public var startScale:*;
        public var character:*;
        public var projectile:*;

        public function NSpecBomb_119()
        {
            super();
            addFrameScript(0, this.frame1, 26, this.frame27, 58, this.frame59, 63, this.frame64);
        }

        public function resize(_arg_1:*=null):*
        {
            this.scale = this.character.getScale().x;
            SSF2API.print(this.scale);
            this.self.setScale((this.scale / this.startScale), (this.scale / this.startScale));
        }

        public function deleteBomb(_arg_1:*=null):*
        {
            if (!(this.self.isDisposed()) && (_arg_1.data.caller.getCurrentAnimation() != "b") && (_arg_1.data.caller.getCurrentAnimation() != "b_air"))
            {
                this.self.destroy();
                this.character.setGlobalVariable("bombCharge", null);
            };
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            if (SSF2API.isReady() && this.self)
            {
                this.character = this.self.getOwner();
            };
            this.projectile = null;
            if (this.self && SSF2API.isReady())
            {
                this.projectile = this.self;
                SSF2API.print("okay here's your bomb");
                this.self.faceRight();
                this.character.setGlobalVariable("NSpecCharge", 1);
                this.startScale = this.self.getScale().x;
                SSF2API.print(this.startScale);
                this.self.createTimer(1, -1, this.resize);
                this.character.addEventListener(SSF2Event.STATE_CHANGE, this.deleteBomb);
                SSF2API.print(((("character is " + this.character) + ", projectile is ") + this.self));
            };
        }

        internal function frame27():*
        {
            this.character.setGlobalVariable("NSpecCharge", 2);
        }

        internal function frame59():*
        {
            this.character.setGlobalVariable("NSpecCharge", 3);
        }

        internal function frame64():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

