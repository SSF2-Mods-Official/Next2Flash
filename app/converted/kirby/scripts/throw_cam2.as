package
{
    import flash.display.MovieClip;

    public dynamic class throw_cam2 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var self:*;
        public var ready:*;
        public var character:*;

        public function throw_cam2()
        {
            super();
            addFrameScript(0, this.frame1, 29, this.frame30);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            this.ready = false;
            if (SSF2API.isReady() && this.self)
            {
                this.character = this.self.getOwner();
                this.self.addToCamera();
            };
        }

        internal function frame30():*
        {
            this.self.removeFromCamera();
        }


    }
}

